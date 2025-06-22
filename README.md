# projetoModular

```text
projeto_modular/
│
├── modulos/                        # Pasta que agrupa todos os módulos do sistema
│   ├── notificacao/
│   │   ├── __init__.py
│   │   └── notificacao.py
│   │
│   ├── lancamento/
│   │   ├── __init__.py
│   │   └── lancamento.py
│   │
│   ├── planejamento/
│   │   ├── __init__.py
│   │   └── planejamento.py
│   │
│   └── relatorio/
│       ├── __init__.py
│       └── relatorio.py
│
├── data/                            # Persistência dos dados entre execuções
│   ├── notificacoes.json
│   ├── lancamentos.json
│   ├── planejamento.json
│   └── relatorios.json
│
├── tests/                           # Testes automatizados (pytest)
│   ├── data/                        # Json de persistência para os testes (para não mexer nos jsons da produção)
│   ├── test_notificacao.py
│   ├── test_lancamento.py
│   ├── test_planejamento.py
│   └── test_relatorio.py
│
├── main.py                          # Arquivo principal que orquestra os módulos
├── pytest.ini                        # Configuração do pytest
├── .gitignore                        # Arquivos e pastas ignoradas no git
└── README.md                         # Documentação do projeto
