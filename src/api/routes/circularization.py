from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import io
import zipfile

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user
from src.scripts.pdf_generator import generate_confirmation_letter
from src.scripts.docx_generator import generate_confirmation_letter_docx
from src.api.utils.email import send_email

router = APIRouter(
    prefix="/circularization",
    tags=["circularization"]
)

@router.post("/clients/{client_id}/logo", status_code=status.HTTP_201_CREATED)
async def upload_client_logo(
    client_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Client
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    content = await file.read()
    client.logo_content = content
    db.commit()
    return {"message": "Logo uploaded successfully"}

@router.post("/engagements/{engagement_id}/generate", response_model=List[schemas.ConfirmationRequestRead])
def create_circularization_requests(
    engagement_id: int,
    requests: List[schemas.ConfirmationRequestCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Engagement
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    new_requests = []
    for req in requests:
        db_req = models.ConfirmationRequest(
            engagement_id=engagement.id,
            type=req.type,
            recipient_name=req.recipient_name,
            recipient_email=req.recipient_email,
            status="generated"
        )
        db.add(db_req)
        new_requests.append(db_req)

    db.commit()
    for req in new_requests:
        db.refresh(req)

    return new_requests

@router.get("/engagements/{engagement_id}/download", response_class=StreamingResponse)
def download_circularization_letters(
    engagement_id: int,
    format: str = "pdf",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Fetch Engagement and Requests
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    requests = db.query(models.ConfirmationRequest).filter(
        models.ConfirmationRequest.engagement_id == engagement.id
    ).all()

    if not requests:
        raise HTTPException(status_code=400, detail="No confirmation requests found. Generate them first.")

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for req in requests:
            if format.lower() == 'docx':
                file_bytes = generate_confirmation_letter_docx(
                    type=req.type,
                    client_data={'name': engagement.client.name},
                    recipient_data={'name': req.recipient_name},
                    date_base=f"31/12/{engagement.year}",
                    logo_bytes=engagement.client.logo_content
                )
                filename = f"{req.type}_{req.recipient_name.replace(' ', '_')}.docx"
            else:
                # Generate PDF
                file_bytes = generate_confirmation_letter(
                    type=req.type,
                    client_data={'name': engagement.client.name},
                    recipient_data={'name': req.recipient_name},
                    date_base=f"31/12/{engagement.year}", # Or handle specific date
                    logo_bytes=engagement.client.logo_content
                )
                filename = f"{req.type}_{req.recipient_name.replace(' ', '_')}.pdf"

            zf.writestr(filename, file_bytes.getvalue())

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=Circularizacoes_{engagement.client.name}.zip"}
    )

@router.post("/engagements/{engagement_id}/send-letters")
async def send_circularization_letters(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Fetch Engagement and Requests
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    requests = db.query(models.ConfirmationRequest).filter(
        models.ConfirmationRequest.engagement_id == engagement.id,
        models.ConfirmationRequest.recipient_email != None
    ).all()

    sent_count = 0
    for req in requests:
        # Generate PDF for attachment
        pdf_bytes = generate_confirmation_letter(
            type=req.type,
            client_data={'name': engagement.client.name},
            recipient_data={'name': req.recipient_name},
            date_base=f"31/12/{engagement.year}",
            logo_bytes=engagement.client.logo_content
        )

        filename = f"{req.type}_{req.recipient_name.replace(' ', '_')}.pdf"

        # Prepare attachment dict for fastapi-mail
        # fastapi-mail expects: {'file': bytes, 'filename': str, 'mime_type': str} (if using dicts)

        attachment = {
            "file": pdf_bytes.getvalue(),
            "filename": filename,
            "mime_type": "application/pdf",
        }

        try:
            await send_email(
                recipients=[req.recipient_email],
                subject=f"Solicitação de Confirmação - {engagement.client.name}",
                body=f"Prezados,<br><br>Segue em anexo solicitação de confirmação de saldos.<br><br>Atenciosamente,<br>AuditFlow",
                attachments=[attachment]
            )
            req.status = "sent"
            sent_count += 1
        except Exception as e:
            print(f"Failed to send email to {req.recipient_email}: {e}")
            req.status = "failed"

    db.commit()
    return {"message": f"Emails queued. Sent {sent_count} emails."}
