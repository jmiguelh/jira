update jira_card
set status_agrupado = case
                        when status = 'Aguardando Aprovação' 	then 'Backlog'
                        when status = 'Aguardando Chamado' 		then 'Systextil'
                        when status = 'Aguardando Desenvolvimento' 	then 'Systextil'
                        when status = 'Aprovado' 			then 'Especificação'
                        when status = 'Aguardando Orçamento' 	then 'Systextil'
                        when status = 'Em andamento' 		then 'Desenvolvimento'
                        when status = 'Especificação' 		then 'Especificação'
                        when status = 'Tarefas pendentes' 		then 'Desenvolvimento'
                        when status = 'Validação BA' 		then 'Desenvolvimento' 
                        when status = 'Aguardando QA' 		then 'Desenvolvimento' 
                        when status = 'Aguardando homologação' 	then 'Homologação'
                        when status = 'Homologando Systextil' 	then 'Systextil'
                        when status = 'Validação em QA' 		then 'Homologação' 
                        when status = 'Aguardando PRD' 		then 'Produção' 
                        when status = 'Concluído' 		then 'Concluído' 
                        when status = 'Concluído Systextil' 	then 'Concluído' 
                        when status = 'Validação em PRD' 		then 'Produção' 
                        when status = 'Aprovação da Especificação' 	then 'Especificação' 
                        when status = 'Homologando' 		then 'Homologação'
                        when status = 'Reprovar Homologação' 	then 'Homologação' 
                        else ""
                      end;

update jira_card
set tipo_agrupado = case
                        when tipo = 'Ajuste' 			then 'Corretivo'
                        when tipo = 'Configuração' 		then 'Evolutivo'
                        when tipo = 'Estudo' 			then 'Evolutivo'
                        when tipo = 'Inconsistência'        	then 'Corretivo'
                        when tipo = 'Melhoria' 		          then 'Evolutivo'
                        when tipo = 'Nova função' 		then 'Evolutivo'
                        else ""
                      end

