import React, { useState, useRef, useEffect } from 'react';
import { X, FileText, Shield } from 'lucide-react';

const TermsText = () => (
    <div className="space-y-4 text-sm text-slate-600 text-justify">
        <p><strong>Última atualização: Dezembro de 2025</strong></p>
        <p>Bem-vindo ao <strong>AuditFlow</strong>, plataforma desenvolvida e operada por <strong>VORCON CONSULTORES ASSOCIADOS LTDA</strong> ("Vorcon Tech"), inscrita no CNPJ sob o nº <strong>52.806.620/0001-16</strong>.</p>

        <h3 className="font-bold text-slate-800">1. Aceitação dos Termos</h3>
        <p>Ao acessar ou criar uma conta no AuditFlow, você concorda expressamente com estes Termos de Uso. Se você não concordar com qualquer disposição destes termos, você não deve acessar ou usar o serviço. O uso continuado da plataforma implica na aceitação irrestrita de quaisquer alterações futuras nestes termos.</p>

        <h3 className="font-bold text-slate-800">2. Descrição do Serviço e Licença</h3>
        <p>O AuditFlow é uma plataforma SaaS (Software as a Service) destinada à gestão de auditorias independentes, fornecendo ferramentas para planejamento, execução e documentação de trabalhos de auditoria. A Vorcon Tech concede a você uma licença limitada, pessoal, não exclusiva, intransferível e revogável para utilizar o serviço apenas para fins profissionais legítimos, de acordo com as normas do CFC e NBC TAs.</p>
        <p>Você não adquire nenhum direito de propriedade intelectual sobre o software ao utilizá-lo.</p>

        <h3 className="font-bold text-slate-800">3. Obrigações e Responsabilidades do Usuário</h3>
        <p>Você é o único responsável por:</p>
        <ul className="list-disc pl-5">
            <li>Manter a confidencialidade de suas credenciais de acesso (login e senha).</li>
            <li>Garantir a veracidade, exatidão e atualização dos dados cadastrais (incluindo CNAI, CRC, CNPJ e dados pessoais).</li>
            <li>Utilizar a plataforma em conformidade com todas as leis aplicáveis, incluindo normas contábeis e de auditoria.</li>
            <li>Não utilizar o serviço para armazenar ou transmitir conteúdo ilegal, malicioso ou que viole direitos de terceiros.</li>
        </ul>

        <h3 className="font-bold text-slate-800">4. Pagamentos e Assinaturas</h3>
        <p>O acesso a certas funcionalidades requer uma assinatura paga. Os pagamentos são processados de forma segura através de nosso parceiro <strong>Asaas</strong>.</p>
        <p>O não pagamento das mensalidades poderá resultar na suspensão temporária ou no cancelamento definitivo do acesso à conta e aos dados nela contidos, após aviso prévio.</p>

        <h3 className="font-bold text-slate-800">5. Limitação de Responsabilidade</h3>
        <p>A Vorcon Tech envida os melhores esforços para garantir a disponibilidade e segurança da plataforma. No entanto, o serviço é fornecido "no estado em que se encontra", sem garantias de que será ininterrupto ou livre de erros.</p>
        <p>Em nenhuma hipótese a Vorcon Tech será responsável por decisões de auditoria, pareceres emitidos, lucros cessantes, perda de dados ou danos indiretos decorrentes do uso da ferramenta. A responsabilidade técnica pelos trabalhos de auditoria é exclusiva do Auditor Responsável.</p>

        <h3 className="font-bold text-slate-800">6. Propriedade Intelectual</h3>
        <p>Todos os direitos sobre o software, design, código-fonte e marcas associadas ao AuditFlow são propriedade exclusiva da Vorcon Tech. A engenharia reversa, cópia ou distribuição não autorizada é estritamente proibida.</p>

        <h3 className="font-bold text-slate-800">7. Rescisão</h3>
        <p>Podemos encerrar ou suspender seu acesso imediatamente, sem aviso prévio ou responsabilidade, por qualquer motivo, inclusive, sem limitação, se você violar os Termos.</p>

        <h3 className="font-bold text-slate-800">8. Disposições Finais e Contato</h3>
        <p>Estes termos são regidos pelas leis da República Federativa do Brasil. Fica eleito o foro da comarca da sede da Vorcon Tech para dirimir quaisquer dúvidas.</p>
        <p>Dúvidas? Entre em contato: <strong>luizviana@vorcon.com.br</strong>.</p>

        <div className="h-16"></div>
        <p className="text-xs text-slate-400 text-center">Final dos Termos de Uso.</p>
    </div>
);

const PrivacyText = () => (
    <div className="space-y-4 text-sm text-slate-600 text-justify">
        <p><strong>Política de Privacidade e Proteção de Dados - LGPD</strong></p>
        <p>A <strong>VORCON TECH</strong> (CNPJ 52.806.620/0001-16) preza pela sua privacidade e assume o compromisso de proteger os dados pessoais que você nos fornece, atuando em total conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).</p>

        <h3 className="font-bold text-slate-800">1. Dados Coletados</h3>
        <p>Para a prestação dos serviços, coletamos e processamos os seguintes dados:</p>
        <ul className="list-disc pl-5">
            <li><strong>Dados Cadastrais:</strong> Nome completo, endereço de e-mail corporativo, CPF, cargo/função.</li>
            <li><strong>Dados da Empresa:</strong> Razão Social, CNPJ, Endereço, Registro no CRC.</li>
            <li><strong>Dados Profissionais:</strong> Número de registro CNAI, Validade do CNAI/CRC, CVM.</li>
            <li><strong>Dados Financeiros:</strong> Informações necessárias para faturamento (processadas de forma criptografada pelo Gateway).</li>
            <li><strong>Dados de Uso:</strong> Logs de acesso, endereço IP e interações com a plataforma para fins de segurança e auditoria.</li>
        </ul>

        <h3 className="font-bold text-slate-800">2. Finalidade do Tratamento</h3>
        <p>Utilizamos seus dados para as seguintes finalidades legítimas:</p>
        <ul className="list-disc pl-5">
            <li>Fornecer, operar e manter os serviços do AuditFlow.</li>
            <li>Processar transações, faturas e assinaturas via Asaas.</li>
            <li>Verificar a legitimidade do cadastro (Compliance) e prevenir fraudes.</li>
            <li>Cumprir obrigações legais e regulatórias (ex: exigências do CFC, Receita Federal).</li>
            <li>Enviar comunicações importantes sobre sua conta, atualizações de segurança e melhorias no serviço.</li>
        </ul>

        <h3 className="font-bold text-slate-800">3. Compartilhamento de Dados</h3>
        <p>Não vendemos, alugamos ou negociamos seus dados pessoais com terceiros. O compartilhamento ocorre apenas nas seguintes hipóteses:</p>
        <ul className="list-disc pl-5">
            <li><strong>Provedores de Serviço:</strong> Com parceiros essenciais para a operação (ex: processamento de pagamentos, hospedagem em nuvem), que estão obrigados a manter sigilo e segurança.</li>
            <li><strong>Obrigação Legal:</strong> Quando exigido por lei, ordem judicial ou solicitação de autoridades competentes (ex: CFC, CVM, Polícia Federal).</li>
        </ul>

        <h3 className="font-bold text-slate-800">4. Segurança dos Dados</h3>
        <p>Adotamos medidas técnicas e organizacionais robustas para proteger seus dados contra acesso não autorizado, perda, alteração ou destruição. Utilizamos criptografia (SSL/TLS) em todas as comunicações e o banco de dados é protegido em ambiente seguro.</p>

        <h3 className="font-bold text-slate-800">5. Retenção de Dados</h3>
        <p>Reteremos seus dados pessoais apenas pelo tempo necessário para cumprir as finalidades para as quais foram coletados, inclusive para fins de cumprimento de quaisquer obrigações legais, contratuais, de prestação de contas ou requisição de autoridades competentes.</p>

        <h3 className="font-bold text-slate-800">6. Seus Direitos (Titular dos Dados)</h3>
        <p>Você possui diversos direitos garantidos pela LGPD, incluindo:</p>
        <ul className="list-disc pl-5">
            <li>Confirmação da existência de tratamento;</li>
            <li>Acesso aos dados;</li>
            <li>Correção de dados incompletos, inexatos ou desatualizados;</li>
            <li>Revogação do consentimento (quando aplicável);</li>
            <li>Exclusão de dados (respeitados os prazos legais de guarda).</li>
        </ul>
        <p>Para exercer seus direitos, entre em contato com nosso Encarregado de Dados (DPO) pelo e-mail: <strong>luizviana@vorcon.com.br</strong>.</p>

        <div className="h-16"></div>
        <p className="text-xs text-slate-400 text-center">Final da Política de Privacidade.</p>
    </div>
);

export const LegalModal = ({ title, type, isOpen, onClose, onAccept }) => {
    const [scrolledToBottom, setScrolledToBottom] = useState(false);
    const contentRef = useRef(null);

    const checkScroll = () => {
        if (contentRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = contentRef.current;
            // More lenient tolerance (50px) to catch the end easily
            // Also explicitly check if content fits without scrolling (scrollHeight <= clientHeight)
            if (scrollHeight <= clientHeight || scrollTop + clientHeight >= scrollHeight - 50) {
                setScrolledToBottom(true);
            }
        }
    };

    // Check on mount and on open
    useEffect(() => {
        if (isOpen) {
            // Check immediately in case it fits
            setTimeout(checkScroll, 100);
        }
    }, [isOpen]);

    const handleScroll = () => {
        checkScroll();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
            <div className="bg-white rounded-lg shadow-2xl max-w-lg w-full flex flex-col max-h-[85vh]">
                <div className="p-4 border-b border-slate-100 flex justify-between items-center">
                    <h2 className="text-lg font-bold text-slate-800 flex items-center">
                        {type === 'terms' ? <FileText className="w-5 h-5 mr-2 text-blue-600" /> : <Shield className="w-5 h-5 mr-2 text-green-600" />}
                        {title}
                    </h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div
                    ref={contentRef}
                    onScroll={handleScroll}
                    className="p-6 overflow-y-auto flex-1 bg-slate-50"
                >
                    {type === 'terms' ? <TermsText /> : <PrivacyText />}
                </div>

                <div className="p-4 border-t border-slate-100 bg-white">
                    <div className="flex items-center mb-4">
                        <input
                            type="checkbox"
                            id={`accept-${type}`}
                            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:opacity-50"
                            checked={scrolledToBottom} // Visual feedback
                            readOnly
                        />
                        <label htmlFor={`accept-${type}`} className={`ml-2 text-sm ${scrolledToBottom ? "text-green-600 font-medium" : "text-slate-500"}`}>
                            {scrolledToBottom ? "Obrigado por ler!" : "Role até o fim para desbloquear o aceite."}
                        </label>
                    </div>
                    <button
                        onClick={onAccept}
                        disabled={!scrolledToBottom}
                        className={`w-full py-3 px-4 rounded-lg font-bold text-white transition-all transform active:scale-95 ${scrolledToBottom
                            ? 'bg-blue-600 hover:bg-blue-700 shadow-md ring-2 ring-blue-300 ring-opacity-50'
                            : 'bg-slate-300 cursor-not-allowed'
                            }`}
                    >
                        {scrolledToBottom ? "Li e Concordo" : "Leia até o final"}
                    </button>
                </div>
            </div>
        </div>
    );
};
