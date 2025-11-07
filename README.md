# Dashbord de acompanhamento de um projeto no Jira

O projeto foi desenvolvido de Python 3.11.

## Bibliotecas

- [atlassian-python-api](https://pypi.org/project/atlassian-python-api/) para a conexão a [API do Jira](https://docs.atlassian.com/software/jira/docs/api/REST/8.5.0/#api/2);
- [Streamlit](https://streamlit.io/) para a construção do dashborad;
- [Plotly](https://plotly.com/python/) para a elaboração dos gráficos;
- [Pony](https://ponyorm.org/) como ORM;
- [Request](https://requests.readthedocs.io/en/latest/);
- [python-dotenv](https://pypi.org/project/python-dotenv/).

## Execução

Para buscar os dados do Jira precisamos executar ``` python jira.py ```

E o para exibir o painel ``` streamlit run app.py ```
