import React, { useState, useEffect } from 'react';
import { CheckCircle, CreditCard } from 'lucide-react';
import { getPlans, getMySubscription, subscribeToPlan } from '../services/clientService';

const BillingPage = () => {
    const [plans, setPlans] = useState([]);
    const [mySub, setMySub] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [plansData, subData] = await Promise.all([getPlans(), getMySubscription()]);
            setPlans(plansData);
            setMySub(subData);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSubscribe = async (planId) => {
        if (!confirm("Confirmar alteração de plano?")) return;
        try {
            setLoading(true);
            await subscribeToPlan(planId);
            await loadData();
        } catch (err) {
            alert(err.message);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8">Carregando...</div>;

    const currentPlanId = mySub?.subscription?.plan_id;

    return (
        <div className="max-w-6xl mx-auto p-6">
            <h1 className="text-3xl font-bold text-slate-800 mb-2">Assinatura e Planos</h1>
            <p className="text-slate-600 mb-8">Gerencie o plano da sua firma e visualize faturas.</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                {plans.map(plan => {
                    const isCurrent = plan.id === currentPlanId;
                    return (
                        <div key={plan.id} className={`bg-white rounded-xl shadow-sm border p-6 flex flex-col ${isCurrent ? 'border-blue-500 ring-2 ring-blue-500 ring-opacity-20' : 'border-slate-200'}`}>
                            <div className="mb-4">
                                <h3 className="text-xl font-bold text-slate-900">{plan.name}</h3>
                                <div className="text-3xl font-bold text-slate-900 mt-2">R$ {plan.price}<span className="text-sm font-normal text-slate-500">/mês</span></div>
                                <p className="text-sm text-slate-500 mt-2">{plan.description}</p>
                            </div>
                            <ul className="space-y-3 mb-8 flex-1">
                                {plan.features.map((feat, i) => (
                                    <li key={i} className="flex items-start text-sm text-slate-600">
                                        <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                                        {feat}
                                    </li>
                                ))}
                            </ul>
                            <button
                                onClick={() => !isCurrent && handleSubscribe(plan.id)}
                                disabled={isCurrent}
                                className={`w-full py-2 rounded-lg font-medium transition-colors ${isCurrent ? 'bg-green-100 text-green-700 cursor-default' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
                            >
                                {isCurrent ? 'Plano Atual' : 'Selecionar'}
                            </button>
                        </div>
                    );
                })}
            </div>

            {/* Invoices */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center">
                    <CreditCard className="w-5 h-5 text-slate-500 mr-2" />
                    <h2 className="text-lg font-bold text-slate-800">Histórico de Pagamentos</h2>
                </div>
                <table className="min-w-full divide-y divide-slate-200">
                    <thead>
                        <tr className="bg-slate-50">
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Data</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Valor</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase">Fatura</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-200">
                        {mySub?.payments?.map(pay => (
                            <tr key={pay.id}>
                                <td className="px-6 py-4 text-sm text-slate-600">{new Date(pay.date).toLocaleDateString()}</td>
                                <td className="px-6 py-4 text-sm text-slate-900 font-medium">R$ {pay.amount.toFixed(2)}</td>
                                <td className="px-6 py-4">
                                    <span className="px-2 py-1 rounded-full text-xs font-bold uppercase bg-green-100 text-green-800">{pay.status}</span>
                                </td>
                                <td className="px-6 py-4 text-right text-sm text-blue-600 hover:underline cursor-pointer">Download PDF</td>
                            </tr>
                        ))}
                        {!mySub?.payments?.length && (
                            <tr><td colSpan="4" className="px-6 py-4 text-center text-slate-500">Nenhum pagamento registrado.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default BillingPage;
