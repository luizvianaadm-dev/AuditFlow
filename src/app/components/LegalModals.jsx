import React, { useState, useRef, useEffect } from 'react';
import { X, FileText, Shield } from 'lucide-react';

const TermsText = () => (
    <div className="space-y-4 text-sm text-slate-600">
        <p><strong>Última atualização: Dezembro de 2025</strong></p>
        <p>Bem-vindo ao <strong>AuditFlow</strong>, plataforma desenvolvida e operada por <strong>VORCON CONSULTORES ASSOCIADOS LTDA</strong> ("Vorcon Tech"), inscrita no CNPJ sob o nº <strong>52.806.620/0001-16</strong>.</p>

        <h3 className="font-bold text-slate-800">1. Aceitação</h3>
        <p>Ao criar uma conta, você concorda em cumprir estes Termos de Uso. Se você não concordar, não poderá usar o serviço.</p>

        <h3 className="font-bold text-slate-800">2. O Serviço</h3>
        <p>O AuditFlow é um SaaS para gestão de auditorias. A Vorcon Tech concede a você uma licença limitada, não exclusiva e revogável para uso profissional.</p>

        <h3 className="font-bold text-slate-800">3. Responsabilidades do Usuário</h3>
        <p>Você é responsável por manter a confidencialidade de suas credenciais e pela veracidade dos dados inseridos (CNAI, CVM, etc.). O uso para fins ilegais é estritamente proibido.</p>

        <h3 className="font-bold text-slate-800">4. Pagamentos</h3>
        <p>Os pagamentos são processados via Gateway (Asaas). O não pagamento pode resultar na suspensão do acesso.</p>

        <h3 className="font-bold text-slate-800">5. Limitação de Responsabilidade</h3>
        <p>A Vorcon Tech não se responsabiliza por conclusões de auditoria errôneas baseadas no uso da ferramenta. A responsabilidade técnica é do Auditor Responsável.</p>

        <h3 className="font-bold text-slate-800">6. Contato</h3>
        <p>Dúvidas? Entre em contato: <strong>luizviana@vorcon.com.br</strong>.</p>

        {/* Placeholder for long scroll */}
        <div className="h-32"></div>
        <p className="text-xs text-slate-400">Final dos Termos.</p>
    </div>
);

const PrivacyText = () => (
    <div className="space-y-4 text-sm text-slate-600">
        <p><strong>Política de Privacidade - LGPD</strong></p>
        <p>A <strong>VORCON TECH</strong> (CNPJ 52.806.620/0001-16) respeita sua privacidade e atua conforme a Lei Geral de Proteção de Dados (Lei 13.709/2018).</p>

        <h3 className="font-bold text-slate-800">1. Coleta de Dados</h3>
        <p>Coletamos dados cadastrais (Nome, Email, CPF/CNPJ, CNAI) para identificação e faturamento.</p>

        <h3 className="font-bold text-slate-800">2. Finalidade</h3>
        <p>Seus dados são usados para: prover o serviço, processar pagamentos (via Asaas), e cumprir obrigações legais (CFC/CVM).</p>

        <h3 className="font-bold text-slate-800">3. Compartilhamento</h3>
        <p>Não vendemos seus dados. Compartilhamos apenas com parceiros essenciais (ex: Gateway de Pagamento) e autoridades quando requisitado legalmente.</p>

        <h3 className="font-bold text-slate-800">4. Seus Direitos</h3>
        <p>Você pode solicitar a exclusão, correção ou portabilidade de seus dados a qualquer momento pelo email <strong>luizviana@vorcon.com.br</strong>.</p>

        {/* Placeholder for long scroll */}
        <div className="h-32"></div>
        <p className="text-xs text-slate-400">Final da Política.</p>
    </div>
);

export const LegalModal = ({ title, type, isOpen, onClose, onAccept }) => {
    const [scrolledToBottom, setScrolledToBottom] = useState(false);
    const contentRef = useRef(null);

    const handleScroll = () => {
        if (contentRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = contentRef.current;
            if (scrollTop + clientHeight >= scrollHeight - 20) { // Tolerance
                setScrolledToBottom(true);
            }
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
            <div className="bg-white rounded-lg shadow-2xl max-w-lg w-full flex flex-col max-h-[80vh]">
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
                        <label htmlFor={`accept-${type}`} className="ml-2 text-sm text-slate-600">
                            {scrolledToBottom ? "Leitura concluída." : "Role até o fim para aceitar."}
                        </label>
                    </div>
                    <button
                        onClick={onAccept}
                        disabled={!scrolledToBottom}
                        className={`w-full py-2 px-4 rounded-lg font-bold text-white transition-all ${scrolledToBottom
                                ? 'bg-blue-600 hover:bg-blue-700 shadow-md'
                                : 'bg-slate-300 cursor-not-allowed'
                            }`}
                    >
                        Li e Concordo
                    </button>
                </div>
            </div>
        </div>
    );
};
