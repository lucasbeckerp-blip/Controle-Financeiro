from flask import Flask, render_template_string, request, session, jsonify
import json
import os
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DATA_FILE = 'dados_financeiros.json'

DADOS_PADRAO = {
    'receitas': [
        {'data': '01/03', 'valor': 3000, 'categoria': 'Salário', 'descricao': 'Salário mensal'},
        {'data': '15/03', 'valor': 500, 'categoria': 'Freelance', 'descricao': 'Projeto freelance'},
    ],
    'despesas': [
        {'data': '02/03', 'valor': 1200, 'categoria': 'Moradia', 'tipo': 'Fixa', 'status': 'Pago', 'descricao': 'Aluguel'},
        {'data': '05/03', 'valor': 450, 'categoria': 'Alimentação', 'tipo': 'Variável', 'status': 'Pago', 'descricao': 'Supermercado'},
        {'data': '07/03', 'valor': 150, 'categoria': 'Transporte', 'tipo': 'Fixa', 'status': 'Pago', 'descricao': 'Gasolina'},
        {'data': '10/03', 'valor': 200, 'categoria': 'Assinaturas', 'tipo': 'Fixa', 'status': 'Pago', 'descricao': 'Netflix, Spotify'},
    ],
    'meta': 500
}

def carregar_dados():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DADOS_PADRAO
    return DADOS_PADRAO

def salvar_dados(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Financeiro</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            font-size: 28px;
            color: #333;
        }

        .logout-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }

        .logout-btn:hover {
            background: #c0392b;
        }

        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .metric-label {
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }

        .metric-receita .metric-value { color: #27ae60; }
        .metric-despesa .metric-value { color: #e74c3c; }
        .metric-saldo .metric-value { color: #3498db; }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .chart-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .chart-card h3 {
            margin-bottom: 15px;
            color: #333;
            font-size: 16px;
        }

        .form-section {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }

        .form-section h3 {
            margin-bottom: 20px;
            color: #333;
            font-size: 18px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
            font-size: 14px;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: background 0.3s;
        }

        .btn:hover {
            background: #5568d3;
        }

        .btn-danger {
            background: #e74c3c;
        }

        .btn-danger:hover {
            background: #c0392b;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        .table thead {
            background: #f5f5f5;
        }

        .table th {
            padding: 12px;
            text-align: left;
            color: #555;
            font-weight: 500;
            border-bottom: 2px solid #ddd;
            font-size: 13px;
        }

        .table td {
            padding: 12px;
            border-bottom: 1px solid #eee;
            font-size: 14px;
        }

        .table tbody tr:hover {
            background: #f9f9f9;
        }

        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }

        .badge-fixa {
            background: #ffd700;
            color: #333;
        }

        .badge-variavel {
            background: #87ceeb;
            color: #333;
        }

        .badge-pago {
            background: #90ee90;
            color: #333;
        }

        .badge-pendente {
            background: #ffb6c6;
            color: #333;
        }

        .success {
            color: #27ae60;
        }

        .danger {
            color: #e74c3c;
        }

        .info {
            color: #3498db;
        }

        .tab-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
        }

        .tab-btn {
            background: none;
            border: none;
            padding: 10px 15px;
            cursor: pointer;
            color: #999;
            font-weight: 500;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
        }

        .tab-btn.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }

            .header {
                flex-direction: column;
                gap: 15px;
            }

            .table {
                font-size: 12px;
            }

            .table th, .table td {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Painel Financeiro</h1>
            <form action="/logout" method="POST" style="display: inline;">
                <button type="submit" class="logout-btn">Sair</button>
            </form>
        </div>

        <!-- MÉTRICAS -->
        <div class="metrics">
            <div class="metric-card metric-receita">
                <div class="metric-label">Receita Total</div>
                <div class="metric-value" id="totalReceita">R$ 0,00</div>
            </div>
            <div class="metric-card metric-despesa">
                <div class="metric-label">Despesas</div>
                <div class="metric-value" id="totalDespesa">R$ 0,00</div>
            </div>
            <div class="metric-card metric-saldo">
                <div class="metric-label">Saldo</div>
                <div class="metric-value" id="saldoTotal">R$ 0,00</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">% Gasto</div>
                <div class="metric-value" id="percentualGasto">0%</div>
            </div>
        </div>

        <!-- GRÁFICOS -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Despesas por Categoria</h3>
                <div style="position: relative; height: 300px;">
                    <canvas id="chartCategoria"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3>Receita vs Despesa</h3>
                <div style="position: relative; height: 300px;">
                    <canvas id="chartComparacao"></canvas>
                </div>
            </div>
        </div>

        <!-- METAS -->
        <div class="form-section">
            <h3>Meta de Economia</h3>
            <div class="form-row">
                <div class="form-group">
                    <label>Meta Mensal (R$)</label>
                    <input type="number" id="metaInput" value="500" step="10">
                </div>
                <div style="display: flex; align-items: flex-end;">
                    <button class="btn" onclick="salvarMeta()">Salvar Meta</button>
                </div>
            </div>
            <div style="margin-top: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span>Economia Realizada</span>
                    <span id="economiaRealizada" class="success" style="font-weight: bold;">R$ 0,00</span>
                </div>
                <div style="background: #eee; height: 20px; border-radius: 10px; overflow: hidden;">
                    <div id="barraProgresso" style="height: 100%; background: linear-gradient(90deg, #27ae60, #2ecc71); width: 0%; transition: width 0.3s;"></div>
                </div>
                <div style="text-align: center; margin-top: 10px; color: #666; font-size: 13px;">
                    <span id="percentualMeta">0%</span> da meta
                </div>
            </div>
        </div>

        <!-- ABAS -->
        <div class="form-section">
            <div class="tab-buttons">
                <button class="tab-btn active" onclick="mostrarAba('receitas')">Receitas</button>
                <button class="tab-btn" onclick="mostrarAba('despesas')">Despesas</button>
            </div>

            <!-- ABA RECEITAS -->
            <div id="receitas" class="tab-content active">
                <h3>Adicionar Receita</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label>Data</label>
                        <input type="date" id="receitaData">
                    </div>
                    <div class="form-group">
                        <label>Descrição</label>
                        <input type="text" id="receitaDescricao" placeholder="Ex: Salário, Freelance...">
                    </div>
                    <div class="form-group">
                        <label>Categoria</label>
                        <select id="receitaCategoria">
                            <option>Salário</option>
                            <option>Freelance</option>
                            <option>Extra</option>
                            <option>Investimentos</option>
                            <option>Outros</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Valor (R$)</label>
                        <input type="number" id="receitaValor" placeholder="0,00" step="0.01">
                    </div>
                </div>
                <button class="btn" onclick="adicionarReceita()">Adicionar Receita</button>

                <h3 style="margin-top: 30px;">Receitas Registradas</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Descrição</th>
                            <th>Categoria</th>
                            <th>Valor</th>
                            <th>Ação</th>
                        </tr>
                    </thead>
                    <tbody id="tabelaReceitas"></tbody>
                </table>
            </div>

            <!-- ABA DESPESAS -->
            <div id="despesas" class="tab-content">
                <h3>Adicionar Despesa</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label>Data</label>
                        <input type="date" id="despesaData">
                    </div>
                    <div class="form-group">
                        <label>Descrição</label>
                        <input type="text" id="despesaDescricao" placeholder="Ex: Aluguel, Supermercado...">
                    </div>
                    <div class="form-group">
                        <label>Categoria</label>
                        <select id="despesaCategoria">
                            <option>Alimentação</option>
                            <option>Transporte</option>
                            <option>Moradia</option>
                            <option>Lazer</option>
                            <option>Assinaturas</option>
                            <option>Saúde</option>
                            <option>Outros</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Tipo</label>
                        <select id="despesaTipo">
                            <option>Fixa</option>
                            <option>Variável</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Status</label>
                        <select id="despesaStatus">
                            <option>Pago</option>
                            <option>Pendente</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Valor (R$)</label>
                        <input type="number" id="despesaValor" placeholder="0,00" step="0.01">
                    </div>
                </div>
                <button class="btn" onclick="adicionarDespesa()">Adicionar Despesa</button>

                <h3 style="margin-top: 30px;">Despesas Registradas</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Descrição</th>
                            <th>Categoria</th>
                            <th>Tipo</th>
                            <th>Status</th>
                            <th>Valor</th>
                            <th>Ação</th>
                        </tr>
                    </thead>
                    <tbody id="tabelaDespesas"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let dados = {};

        function formatarMoeda(valor) {
            return 'R$ ' + valor.toFixed(2).replace('.', ',').replace(/\\B(?=(\\d{3})+(?!\\d))/g, '.');
        }

        function carregarDados() {
            fetch('/api/dados')
                .then(r => r.json())
                .then(d => {
                    dados = d;
                    atualizarUI();
                });
        }

        function atualizarUI() {
            const receita = dados.receitas.reduce((a, r) => a + r.valor, 0);
            const despesa = dados.despesas.reduce((a, d) => a + d.valor, 0);
            const saldo = receita - despesa;
            const percentual = receita > 0 ? Math.round((despesa / receita) * 100) : 0;

            document.getElementById('totalReceita').textContent = formatarMoeda(receita);
            document.getElementById('totalDespesa').textContent = formatarMoeda(despesa);
            document.getElementById('saldoTotal').textContent = formatarMoeda(saldo);
            document.getElementById('saldoTotal').style.color = saldo >= 0 ? '#27ae60' : '#e74c3c';
            document.getElementById('percentualGasto').textContent = percentual + '%';

            const meta = dados.meta || 500;
            const economia = Math.max(0, saldo);
            const percentualMeta = Math.min(100, Math.round((economia / meta) * 100));
            document.getElementById('economiaRealizada').textContent = formatarMoeda(economia);
            document.getElementById('barraProgresso').style.width = percentualMeta + '%';
            document.getElementById('percentualMeta').textContent = percentualMeta;
            document.getElementById('metaInput').value = meta;

            document.getElementById('tabelaReceitas').innerHTML = dados.receitas.map((r, i) => `
                <tr>
                    <td>${r.data}</td>
                    <td>${r.descricao}</td>
                    <td>${r.categoria}</td>
                    <td class="success">${formatarMoeda(r.valor)}</td>
                    <td><button class="btn btn-danger" style="padding: 5px 10px; font-size: 12px;" onclick="deletarReceita(${i})">Deletar</button></td>
                </tr>
            `).join('');

            document.getElementById('tabelaDespesas').innerHTML = dados.despesas.map((d, i) => `
                <tr>
                    <td>${d.data}</td>
                    <td>${d.descricao}</td>
                    <td>${d.categoria}</td>
                    <td><span class="badge badge-${d.tipo.toLowerCase()}">${d.tipo}</span></td>
                    <td><span class="badge badge-${d.status.toLowerCase()}">${d.status}</span></td>
                    <td class="danger">${formatarMoeda(d.valor)}</td>
                    <td><button class="btn btn-danger" style="padding: 5px 10px; font-size: 12px;" onclick="deletarDespesa(${i})">Deletar</button></td>
                </tr>
            `).join('');

            renderizarGraficos(receita, despesa);
        }

        function renderizarGraficos(receita, despesa) {
            const categorias = [...new Set(dados.despesas.map(d => d.categoria))];
            const valores = categorias.map(c => dados.despesas.filter(d => d.categoria === c).reduce((a, d) => a + d.valor, 0));
            const cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'];

            if (window.chartCat) window.chartCat.destroy();
            window.chartCat = new Chart(document.getElementById('chartCategoria'), {
                type: 'doughnut',
                data: {
                    labels: categorias,
                    datasets: [{
                        data: valores,
                        backgroundColor: cores.slice(0, categorias.length)
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });

            if (window.chartComp) window.chartComp.destroy();
            window.chartComp = new Chart(document.getElementById('chartComparacao'), {
                type: 'bar',
                data: {
                    labels: ['Receita', 'Despesa'],
                    datasets: [{
                        data: [receita, despesa],
                        backgroundColor: ['#27ae60', '#e74c3c'],
                        borderRadius: 6
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { beginAtZero: true } }
                }
            });
        }

        function adicionarReceita() {
            const receita = {
                data: document.getElementById('receitaData').value,
                descricao: document.getElementById('receitaDescricao').value,
                categoria: document.getElementById('receitaCategoria').value,
                valor: parseFloat(document.getElementById('receitaValor').value) || 0
            };
            if (!receita.data || !receita.descricao || receita.valor <= 0) {
                alert('Preencha todos os campos corretamente!');
                return;
            }
            fetch('/api/receita', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(receita) })
                .then(() => carregarDados());
            document.getElementById('receitaData').value = '';
            document.getElementById('receitaDescricao').value = '';
            document.getElementById('receitaValor').value = '';
        }

        function adicionarDespesa() {
            const despesa = {
                data: document.getElementById('despesaData').value,
                descricao: document.getElementById('despesaDescricao').value,
                categoria: document.getElementById('despesaCategoria').value,
                tipo: document.getElementById('despesaTipo').value,
                status: document.getElementById('despesaStatus').value,
                valor: parseFloat(document.getElementById('despesaValor').value) || 0
            };
            if (!despesa.data || !despesa.descricao || despesa.valor <= 0) {
                alert('Preencha todos os campos corretamente!');
                return;
            }
            fetch('/api/despesa', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(despesa) })
                .then(() => carregarDados());
            document.getElementById('despesaData').value = '';
            document.getElementById('despesaDescricao').value = '';
            document.getElementById('despesaValor').value = '';
        }

        function deletarReceita(idx) {
            if (confirm('Tem certeza?')) {
                fetch(`/api/receita/${idx}`, { method: 'DELETE' }).then(() => carregarDados());
            }
        }

        function deletarDespesa(idx) {
            if (confirm('Tem certeza?')) {
                fetch(`/api/despesa/${idx}`, { method: 'DELETE' }).then(() => carregarDados());
            }
        }

        function salvarMeta() {
            const meta = parseFloat(document.getElementById('metaInput').value) || 500;
            fetch('/api/meta', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ meta }) })
                .then(() => carregarDados());
        }

        function mostrarAba(aba) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(aba).classList.add('active');
            event.target.classList.add('active');
        }

        const hoje = new Date().toISOString().split('T')[0];
        document.getElementById('receitaData').value = hoje;
        document.getElementById('despesaData').value = hoje;

        carregarDados();
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '123456':
            session['logged_in'] = True
            return app.redirect('/dashboard')
        else:
            return render_template_string('''
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Login - Painel Financeiro</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .login-box {
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                        width: 100%;
                        max-width: 400px;
                    }
                    h1 {
                        text-align: center;
                        margin-bottom: 30px;
                        color: #333;
                    }
                    .form-group {
                        margin-bottom: 20px;
                    }
                    label {
                        display: block;
                        margin-bottom: 8px;
                        color: #555;
                        font-weight: 500;
                    }
                    input {
                        width: 100%;
                        padding: 12px;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        font-size: 14px;
                    }
                    input:focus {
                        outline: none;
                        border-color: #667eea;
                        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                    }
                    button {
                        width: 100%;
                        padding: 12px;
                        background: #667eea;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 16px;
                        font-weight: 500;
                        cursor: pointer;
                        transition: background 0.3s;
                    }
                    button:hover {
                        background: #5568d3;
                    }
                    .error {
                        background: #fee;
                        color: #c00;
                        padding: 12px;
                        border-radius: 6px;
                        margin-bottom: 20px;
                        font-size: 14px;
                    }
                    .hint {
                        text-align: center;
                        margin-top: 20px;
                        color: #999;
                        font-size: 12px;
                    }
                </style>
            </head>
            <body>
                <div class="login-box">
                    <h1>💰 Painel Financeiro</h1>
                    <div class="error">Senha incorreta! Tente novamente.</div>
                    <form method="POST">
                        <div class="form-group">
                            <label>Senha:</label>
                            <input type="password" name="password" autofocus required>
                        </div>
                        <button type="submit">Acessar</button>
                    </form>
                    <div class="hint">Senha padrão: 123456</div>
                </div>
            </body>
            </html>
            ''')
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Painel Financeiro</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-box {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                width: 100%;
                max-width: 400px;
            }
            h1 {
                text-align: center;
                margin-bottom: 10px;
                color: #333;
            }
            .subtitle {
                text-align: center;
                color: #999;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                color: #555;
                font-weight: 500;
            }
            input {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            button {
                width: 100%;
                padding: 12px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover {
                background: #5568d3;
            }
            .hint {
                text-align: center;
                margin-top: 20px;
                color: #999;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>💰 Painel Financeiro</h1>
            <p class="subtitle">Seu controle financeiro online</p>
            <form method="POST">
                <div class="form-group">
                    <label>Senha:</label>
                    <input type="password" name="password" autofocus required>
                </div>
                <button type="submit">Acessar</button>
            </form>
            <div class="hint">Senha padrão: 123456</div>
        </div>
    </body>
    </html>
    ''')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return app.redirect('/')
    return render_template_string(HTML_TEMPLATE)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return app.redirect('/')

@app.route('/api/dados')
def get_dados():
    if not session.get('logged_in'):
        return {'error': 'Unauthorized'}, 401
    return jsonify(carregar_dados())

@app.route('/api/receita', methods=['POST'])
def add_receita():
    if not session.get('logged_in'):
        return {'error': 'Unauthorized'}, 401
    dados = carregar_dados()
    dados['receitas'].append(request.json)
    salvar_dados(dados)
    return {'ok': True}

@app.route('/api/receita/<int:idx>', methods=['DELETE'])
def del_receita(idx):
    if not session.get('logged_in'):
        return {'error': 'Unauthorized'}, 401
    dados = carregar_dados()
    if 0 <= idx < len(dados['receitas']):
        dados['receitas'].pop(idx)
        salvar_dados(dados)
    return {'ok': True}

@app.route('/api/despesa', methods=['POST'])
def add_despesa():
    if not session.get('logged_in'):
        return {'error': 'Unauthorized'}, 401
    dados = carregar_dados()
    dados['despesas'].append(request.json)
    salvar_dados(dados)
    return {'ok': True}

@app.route('/api/despesa/<int:idx>', methods=['DELETE'])
def del_despesa(idx):
    if not session.get('logged_in'):
        return {'error': 'Unauthorized'}, 401
    dados = carregar_dados()
    if 0 <= idx < len(dados['despesas']):
        dados['despesas'].pop(idx)
        salvar_dados(dados)
    return {'ok': True}

@app.route('/api/meta', methods=['POST'])
def set_meta():
    if not session.get('logged_in'):
        return {'error': 'Unauthorized'}, 401
    dados = carregar_dados()
    dados['meta'] = request.json.get('meta', 500)
    salvar_dados(dados)
    return {'ok': True}

if __name__ == '__main__':
    salvar_dados(carregar_dados())
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Servidor iniciando...")
    print(f"📱 Acesse em: http://localhost:{port}")
    print(f"🔐 Senha: 123456")
    app.run(host='0.0.0.0', port=port, debug=False)
