import os
import oracledb
import json

# Função para calcular as perdas na colheita
def calcular_perda(area_plantada, produtividade, perdas_percentual):
    total_colhido = area_plantada * produtividade
    perdas = (perdas_percentual / 100) * total_colhido
    return perdas, total_colhido

# Função para registrar dados em JSON
def registrar_dados_em_json(produtores):
    try:
        with open('dados_agro.json', 'w', encoding='utf-8') as file:
            json.dump(produtores, file, indent=4, ensure_ascii=False)
        print(" Dados salvos em dados_agro.json!")
    except Exception as e:
        print(f" Erro ao salvar JSON: {e}")

# Função para carregar dados de um arquivo JSON
def carregar_dados_de_json():
    if os.path.exists('dados_agro.json'):
        try:
            with open('dados_agro.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f" Erro ao ler JSON: {e}")
            return []
    else:
        return []

# Função para inserir dados no banco de dados Oracle
def salvar_no_oracle(produtor, perdas, total_colhido):
    try:
        conn = oracledb.connect(
            user='rm565606',
            password="fiap25",
            dsn='oracle.fiap.com.br:1521/ORCL'
        )
        cursor = conn.cursor()

        sql = """
        INSERT INTO PRODUCAO_CANAVIAL (nome_produtor, area_plantada, perdas, total_colhido)
        VALUES (:1, :2, :3, :4)
        """
        cursor.execute(sql, (
            produtor['nome'],
            produtor['area_plantada'],
            perdas,
            total_colhido
        ))
        conn.commit()
        print(f"Dados do produtor {produtor['nome']} salvos no banco de dados!")
    except Exception as e:
        print(f"Erro ao salvar no banco de dados Oracle: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

# Função principal que executa o fluxo
def main():
    produtores = carregar_dados_de_json()

    print("----- CADASTRAR DADOS -----")
    try:
        nome_produtor = input("Nome do produtor: ")
        area_plantada = float(input("Área plantada (em hectares): "))
        produtividade = float(input("Produtividade (toneladas por hectare): "))
        perdas_percentual = float(input("Percentual de perdas na colheita: "))
    except ValueError:
        print("❌ Erro: Digite apenas números válidos para os campos de área, produtividade e perdas.")
        return

    # Calcular perdas e total colhido
    perdas, total_colhido = calcular_perda(area_plantada, produtividade, perdas_percentual)

    produtor = {
        'nome': nome_produtor,
        'area_plantada': area_plantada,
        'produtividade': produtividade,
        'perdas_percentual': perdas_percentual,
        'perdas': perdas,
        'total_colhido': total_colhido
    }

    produtores.append(produtor)
    registrar_dados_em_json(produtores)
    salvar_no_oracle(produtor, perdas, total_colhido)

    print(f"\n📊 Relatório para o produtor {nome_produtor}:")
    print(f" Área plantada: {area_plantada} hectares")
    print(f"Total colhido: {total_colhido:.2f} toneladas")
    print(f"Perdas na colheita: {perdas:.2f} toneladas")
    print(f"Percentual de perdas: {perdas_percentual}%")

if __name__ == "__main__":
    while True:
        main()
        continuar = input("\nDeseja cadastrar outro produtor? (s/n): ").strip().lower()
        if continuar != 's':
            print("Obrigado por utilizar o nosso sistema. Até a próxima!")
            break
