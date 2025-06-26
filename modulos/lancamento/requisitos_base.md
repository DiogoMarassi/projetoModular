### Requisitos Funcionais do Módulo **Lançamentos Financeiros**

| Código   | Requisito                                                                           | Resposta esperada                        |
| -------- | ----------------------------------------------------------------------------------- | ---------------------------------------- |
| **RF01** | Criar lançamento com tipo (despesa ou receita), valor, data, categoria e descrição. | 201 + dados do lançamento criado.        |
| **RF02** | Caso falha na criação (validação ou campos ausentes).                               | 400 “Dados inválidos ou incompletos.”    |
| **RF03** | Editar lançamento existente (id + novos dados).                                     | —                                        |
| **RF04** | Sucesso na atualização.                                                             | 200 “Lançamento atualizado com sucesso.” |
|          | Dados inválidos.                                                                    | 400                                      |
|          | Lançamento não encontrado.                                                          | 404                                      |
| **RF05** | Remover lançamento pelo identificador.                                              | —                                        |
| **RF06** | Sucesso na remoção.                                                                 | 200 “Lançamento removido com sucesso.”   |
|          | Lançamento não encontrado.                                                          | 404                                      |
| **RF07** | Listar lançamentos com filtros opcionais (valor, data, tipo, categoria).            | —                                        |
| **RF08** | Sucesso na listagem.                                                                | 200 + lista filtrada.                    |
|          | Nenhum lançamento.                                                                  | 404 “Nenhum lançamento encontrado.”      |
| **RF09** | Ordenar listagem por critérios definidos pelo usuário.                              | —                                        |
| **RF10** | Calcular saldo mensal (mês/ano).                                                    | —                                        |
| **RF11** | Sucesso no cálculo.                                                                 | 200 + saldo; data inválida → 400.        |

---

### Especificação do Módulo **Lançamentos Financeiros**&#x20;

**Descrição**
Permite cadastrar, editar, listar e remover lançamentos (receita ou despesa) e calcular o saldo de um mês.

| Função                               | Parâmetros                                                                                                                                                                                                                   | Retornos                                                                                                                                                                      |                 |                      |         |                                                                                                            |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | -------------------- | ------- | ---------------------------------------------------------------------------------------------------------- |
| **criarLancamento(dados)**           | `dados = {descricao: str, valor: float, data: datetime, tipo: str, categoria: str}`<br>• `categoria ∈ {Moradia, Alimentação, Transporte, Saúde, Educação, Lazer, Guardar, Salario, Outros}`<br>• `tipo ∈ {receita, despesa}` | • `{Success: 201, Content: {id, dados}}`<br>• `{Error: 400, Content: "Dados inválidos ou incompletos."}`                                                                      |                 |                      |         |                                                                                                            |
| **editarLancamento(id, novosDados)** | `id: int`<br>`novosDados` mesmo formato de *dados*                                                                                                                                                                           | • `{Success: 200, Content: "Lançamento atualizado com sucesso."}`<br>• `{Error: 400, Content: "Dados inválidos."}`<br>• `{Error: 404, Content: "Lançamento não encontrado."}` |                 |                      |         |                                                                                                            |
| **removerLancamento(id)**            | `id: int`                                                                                                                                                                                                                    | • `{Success: 200, Content: "Lançamento removido com sucesso."}`<br>• `{Error: 404, Content: "Lançamento não encontrado."}`                                                    |                 |                      |         |                                                                                                            |
| **listarLançamentos(filtros)**       | \`filtros = {valor: float                                                                                                                                                                                                    | null, data: datetime                                                                                                                                                          | null, tipo: str | null, categoria: str | null}\` | • `{Success: 200, Content: [ {id, dados} ]}`<br>• `{Error: 404, Content: "Nenhum lançamento encontrado."}` |
| **calcularSaldoMensal(mes, ano)**    | `mes: int`, `ano: int`                                                                                                                                                                                                       | • `{Success: 200, Content: {saldo: float, mes: int, ano: int}}`<br>• `{Error: 400, Content: "Data inválida"}`                                                                 |                 |                      |         |                                                                                                            |

---

### Testes Automatizados do Módulo (**1.1**)&#x20;

| Caso de teste                                      | Expectativa                                                     |
| -------------------------------------------------- | --------------------------------------------------------------- |
| `test_criar_lancamento_sucesso`                    | `Success == 201`, contém `id` e dados corretos.                 |
| `test_criar_lancamento_dados_invalidos`            | `Error == 400`, mensagem “Dados inválidos ou incompletos.”      |
| `test_editar_lancamento_sucesso`                   | `Success == 200`, mensagem “Lançamento atualizado com sucesso.” |
| `test_editar_lancamento_lancamento_nao_encontrado` | `Error == 404`, mensagem “Lançamento não encontrado.”           |
| `test_remover_lancamento_sucesso`                  | `Success == 200`, mensagem “Lançamento removido com sucesso.”   |
| `test_remover_lancamento_nao_encontrado`           | `Error == 404`, mensagem “Lançamento não encontrado.”           |
| `test_listar_lancamentos_com_filtros`              | `Success == 200`, `Content` é lista.                            |
| `test_listar_lancamentos_sem_resultados`           | `Error == 404`, mensagem “Nenhum lançamento encontrado.”        |
| `test_calcular_saldo_mensal_sucesso`               | `Success == 200`, mês e ano corretos.                           |
| `test_calcular_saldo_mensal_data_invalida`         | `Error == 400`, mensagem “Data inválida”.                       |

---

### Testes Integrados Relacionados ao Módulo&#x20;

* **test\_criar\_lancamento\_e\_verificar\_saldo** – cria lançamento e verifica impacto no saldo mensal.
* **test\_criar\_despesa\_excessiva\_dispara\_notificacao** – despesa que ultrapassa limite gera notificação.
* **test\_comparativo\_entre\_anos** – cria lançamentos em dois anos e gera comparativo.
* **test\_gerar\_relatorio\_apos\_lancamentos** – cria lançamentos, gera relatório e verifica consistência de saldo.
