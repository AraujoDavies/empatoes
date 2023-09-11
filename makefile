.PHONY: run help

dev: ## Executa o script localmente em modo interativo
	poetry run ipython -i code/main.py

format: ## padroniza o código e ordena os imports
	poetry run black . 
	poetry run isort .

git: ## MSG - Sobe codigo pro GIT (Necessario usar variavel)
	git add -A
	git commit -m "${MSG}"
	git push
	
build:
	poetry run pyinstaller code/main.py --onefile

help: 
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n make\033[36m\033[0m \033[36m\<command>\033[0m %s\n", $$1, $$2} /^[a-zA-Z_-]+:.*?##/ { printf "\033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf"\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)