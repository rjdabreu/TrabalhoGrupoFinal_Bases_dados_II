# Sistema de Gestão de Biblioteca

## Índice

- [Descrição](#descrição)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
  - [Clonar o Repositório](#clonar-o-repositório)
  - [Configurar o Ambiente](#configurar-o-ambiente)
  - [Configurar a Base de Dados](#configurar-a-base-de-dados)
  - [Executar Serviços de Log e Monitorização](#executar-serviços-de-log-e-monitorização)
  - [Executar a Aplicação](#executar-a-aplicação)



---

## Descrição

O Sistema de Gestão de Biblioteca é uma aplicação que permite a gestão de livros, utilizadores, empréstimos e relatórios de atividades. 
O sistema integra ferramentas modernas para monitorização (Prometheus) e centralização de logs (Elastic Stack).

---

## Funcionalidades
- Gestão de livros, utilizadores e empréstimos.
- Recomendação de livros.
- Logs centralizados com Elastic Stack.
- Monitorização com Prometheus.

---

## Tecnologias
- Python
- Flask
- MySQL
- MongoDB
- Prometheus
- Elastic Stack

---

## Pré-requisitos

Certifique-se de ter os seguintes softwares instalados no seu sistema:

1. **Python** (versão 3.8 ou superior) - (https://www.python.org/downloads/)
2. **MySQL** - (https://dev.mysql.com/downloads/)
3. **MongoDB** - (https://www.mongodb.com/try/download/community)
4. **Elastic Stack** (Elasticsearch, Kibana e Logstash) -(https://www.elastic.co/downloads/)
5. **Prometheus** - (https://prometheus.io/download/)

Adicione os executáveis de todos os softwares ao seu `PATH`, se necessário.

---

## Instalação e Configuração
1. Configurar o Ambiente
pip install -r requirements.txt

2. Configurar o Banco de Dados MySQL
	- Criar a base de dados com o ficheiro Base_Dados.SQL
	- Atualize o ficheiro db_config.py com as suas credenciais

3. Criar o ficheiro logstash.conf com o seguinte conteúdo:
	input {
  file {
    path => "/CAMINHO/PARA O PROJETO/app.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
  }
}
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "application_logs"
  }
  stdout { codec => rubydebug }
}

4. Execute o Logstash: logstash -f logstash.conf

5. Configure o ficheiro prometheus.yml com o seguinte conteúdo:

scrape_configs:
  - job_name: 'biblioteca'
    static_configs:
      - targets: ['localhost:5000']

6. Execute o Prometheus: prometheus --config.file=prometheus.yml

7. Executar a Aplicação Backend execute: python backend.py
   Interface Administrativa execute: python admin_interface.py
### Clonar o Repositório

Abra o terminal e execute:

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
