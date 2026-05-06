# Sistema de Gerenciamento de Produção Leiteira

## 1. Visão Geral do Projeto
- **Nome**: GadoLeiteiro Pro
- **Tipo**: Aplicação web para gestão de fazenda leiteira
- **Funcionalidades principais**: Controle de produção, custos, lucros, ração e animais
- **Usuários**: Gerentes e operadores de fazendas leiteiras

## 2. Especificação UI/UX

### Estrutura de Layout
- Navegação lateral fixa (sidebar)
- Topbar com notifications e user info
- Área principal de conteúdo
- Dashboard com cards de métricas

### Design Visual
- **Cores Primárias**: 
  - Verde escuro: #1B4332 (cabeçalho, sidebar)
  - Verde médio: #2D6A4F (botões primários)
  - Verde claro: #40916C (hover states)
  - Bege: #DDA15E (destaques)
- **Cores Secundárias**:
  - Fundo: #F5F5F5
  - Cards: #FFFFFF
  - Texto: #212529
  - Cinza: #6C757D
- **Tipografia**:
  - Fontes: "Nunito Sans" para textos, "Nunito" para headings
  - Títulos: 24px (h1), 20px (h2), 16px (h3)
  - Corpo: 14px
- **Espaçamento**: 16px base, 24px entre seções

### Componentes
- Cards com sombra leve
- Tabelas com zebra striping
- Formulários com labels flutuantes
- Gráficos com Chart.js
- Modais para confirmações

## 3. Especificação Funcional

### Módulo: Painel (Dashboard)
- **Métricas do dia**:
  - Total produção (litros)
  - Receita (R$)
  - Custo total (R$)
  - Lucro (R$)
- **Gráfico de produção semanal**
- **Alertas de custo alto**

### Módulo: Produção
- **Cadastro diário de leite**:
  - Selecionar animal
  - Informar litros produzidos
  - Data do registro
- **Histórico**: tabela com filtros por período/animal
- **Média por animal**

### Módulo: Ração
- **Cadastro de tipos de ração**:
  - Nome do tipo
  - Preço por kg
- **Registro de consumo diario**:
  - Selecionar animal
  - Selecionar tipo de ração
  - Quantidade (kg)
- **Cálculo automático**: quantidade × preço = custo

### Módulo: Animais (Cadastro)
- Nome do animal
- Brinco (identificador)
- Raça
- Lote
- Data de nascimento
- Status (ativo/inativo)

### Módulo: Relatórios
- **Filtros por período**: data inicial e final
- **Gráficos**:
  - Produção diária (linha)
  - Lucro por período (barra)
  - Custo de ração (pizza)
- **Exportação**: PDF e Excel

### Módulo: Ajustes
- **Preço do leite**:
  - Histórico de preços
  - Edição com data de vigência
  - Cálculos usam preço vigente na data
- **Redefinir dados**:
  - Limpar dados de produção
  - Limpar dados de ração
  - Limpar todos os dados

## 4. Modelos de Dados

### Animal
```
- id: INTEGER PRIMARY KEY
- nome: VARCHAR(100)
- brinco: VARCHAR(50) UNIQUE
- raca: VARCHAR(100)
- lote: VARCHAR(50)
- data_nascimento: DATE
- ativo: BOOLEAN
- created_at: DATETIME
```

### TipoRacao
```
- id: INTEGER PRIMARY KEY
- nome: VARCHAR(100)
- preco_kg: DECIMAL(10,2)
- created_at: DATETIME
```

### ProducaoLeite
```
- id: INTEGER PRIMARY KEY
- animal_id: INTEGER FK
- litros: DECIMAL(10,2)
- data: DATE
- created_at: DATETIME
```

### ConsumoRacao
```
- id: INTEGER PRIMARY KEY
- animal_id: INTEGER FK
- tipo_racao_id: INTEGER FK
- quantidade_kg: DECIMAL(10,2)
- data: DATE
- custo: DECIMAL(10,2)
- created_at: DATETIME
```

### PrecoLeite
```
- id: INTEGER PRIMARY KEY
- preco_litro: DECIMAL(10,4)
- data_vigencia: DATE
- created_at: DATETIME
```

## 5. Rotas

| Rota | Método | Descrição |
|------|--------|-----------|
| / | GET | Dashboard |
| /producao | GET/POST | Lista/Cadastra produção |
| /racao | GET/POST | Lista tipos ração |
| /racao/consumo | GET/POST | Registro consumo |
| /animais | GET/POST | Lista/Cadastra animais |
| /relatorios | GET | Relatórios com filtros |
| /relatorios/exportar | GET | Exporta PDF/Excel |
| /ajustes | GET/POST | Configurações |
| /ajustes/preco | GET/POST | Preço do leite |
| /ajustes/reset | POST | Redefinir dados |

## 6. Stack Tecnológico
- Backend: Flask (Python)
- Banco: SQLite (facilidade deployment)
- Frontend: HTML5, CSS3, JavaScript
- Gráficos: Chart.js
- Exportação: ReportLab (PDF), OpenPyXL (Excel)
- Bootstrap 5 para UI