import typer
from rich import print
import os
import json
from models.SSHKey import SSHKey
from models.SSHConnection import SSHConnection
import questionary

KEYS_DIR = os.path.expanduser("~/.ssh-manager")
KEYS_FILE = os.path.join(KEYS_DIR, "ssh-client-keys.json")
CONNECTIONS_FILE = os.path.join(KEYS_DIR, "ssh-client-connections.json")

def check_if_file_exists(file: str):
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR, mode=0o700)
    if not os.path.exists(file):
        with open(file, "w") as file:
            json.dump([], file)

def save_to_file(file_path: str, item: object):
    #Salva um objeto em um arquivo JSON
    check_if_file_exists(file_path)
    
    try:
        with open(file_path, "r") as file:
            items = json.load(file)
    except json.JSONDecodeError:
        items = []
    
    items.append(item.__dict__)
    
    with open(file_path, "w") as file:
        json.dump(items, file, indent=4)

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        init()

@app.command(name="add-key")
def add_ssh_key(key_path: str = ""):
    #Add a new ssh key to the database
    print("Adicionando nova chave SSH:")
    key_path = input("Caminho absoluto da chave: ")
    key_name = input("Nome da chave (opcional): ")
    key_type = input("Tipo da chave (opcional): ")
    key_description = input("Descrição da chave (opcional): ")

    ssh_key = SSHKey(key_path, key_name, key_type, key_description)
    
    save_to_file(KEYS_FILE, ssh_key)
    
    print(f"Chave SSH adicionada com sucesso: {ssh_key.key_name} \nCaminho: {ssh_key.key_path} \nTipo: {ssh_key.key_type} \nDescrição: {ssh_key.key_description}")


@app.command(name="list-keys")
def list_ssh_keys():
    check_if_file_exists(KEYS_FILE)
    
    try:
        with open(KEYS_FILE, "r") as file:
            keys = json.load(file)
    except json.JSONDecodeError:
        # Se o arquivo estiver corrompido, reinicializa ele
        with open(KEYS_FILE, "w") as file:
            json.dump([], file)
        keys = []
    
    if not keys:
        print("Nenhuma chave SSH encontrada.")
        return
        
    for key in keys:
        print(f"Chave SSH: {key['key_name']} \nCaminho: {key['key_path']} \nTipo: {key['key_type']} \nDescrição: {key['key_description']} \nID: {key['key_id']}\n")

@app.command(name="delete-key")
def delete_ssh_key(key_id: str):
    check_if_file_exists(KEYS_FILE)
    
    try:
        with open(KEYS_FILE, "r") as file:
            keys = json.load(file)
    except json.JSONDecodeError:
        keys = []
    
    keys = [key for key in keys if key['key_id'] != key_id]
    
    with open(KEYS_FILE, "w") as file:
        json.dump(keys, file, indent=4)
    
    print(f"Chave SSH deletada com sucesso: {key_id}")

@app.command(name="add-connection")
def add_ssh_connection():
    print("Adicionando nova conexão SSH:")
    connection_name = input("Nome da conexão (opcional): ")
    connection_key = input("Chave de conexão: ")
    connection_description = input("Descrição da conexão (opcional): ")
    
    ssh_connection = SSHConnection(connection_name, connection_key, connection_description)
    
    check_if_file_exists(CONNECTIONS_FILE)
    
    try:
        with open(CONNECTIONS_FILE, "r") as file:
            connections = json.load(file)
    except json.JSONDecodeError:
        connections = []
    
    connections.append(ssh_connection.__dict__)
    
    with open(CONNECTIONS_FILE, "w") as file:
        json.dump(connections, file, indent=4)

    print(f"Conexão SSH adicionada com sucesso: {ssh_connection.connection_name} \nUsuário: {ssh_connection.connection_user} \nHost: {ssh_connection.connection_host} \nChave de conexão: {ssh_connection.connection_key} \nDescrição: {ssh_connection.connection_description}")


@app.command(name="list-connections")
def list_ssh_connections():
    check_if_file_exists(CONNECTIONS_FILE)
    
    try:
        with open(CONNECTIONS_FILE, "r") as file:
            connections = json.load(file)
    except json.JSONDecodeError:
        connections = []
    
    if not connections:
        print("Nenhuma conexão SSH encontrada.")
        return

    for connection in connections:
        print(f"Conexão SSH: {connection['connection_name']} \nUsuário: {connection['connection_user']} \nHost: {connection['connection_host']} \nChave de conexão: {connection['connection_key']} \nDescrição: {connection['connection_description']} \nID: {connection['connection_id']}\n")


@app.command(name="delete-connection")
def delete_ssh_connection(connection_id: str):
    check_if_file_exists(CONNECTIONS_FILE)
    
    try:
        with open(CONNECTIONS_FILE, "r") as file:
            connections = json.load(file)
    except json.JSONDecodeError:
        connections = []
    
    connections = [connection for connection in connections if connection['connection_id'] != connection_id]    

    with open(CONNECTIONS_FILE, "w") as file:
        json.dump(connections, file, indent=4)
    
    print(f"Conexão SSH deletada com sucesso: {connection_id}")


@app.command(name="add-key-and-connection")
def add_key_and_connection(command: str):
    print("Adicionando nova chave e conexão SSH:")

    key_path = command.split(" ")[2]
    user = command.split(" ")[3].split("@")[0]
    host = command.split(" ")[3].split("@")[1]

    ssh_key = SSHKey(key_path)
    ssh_connection = SSHConnection(connection_name=user, connection_key=f"{user}@{host}")

    save_to_file(KEYS_FILE, ssh_key)
    save_to_file(CONNECTIONS_FILE, ssh_connection)

    print(f"Chave SSH e conexão SSH adicionadas com sucesso: {ssh_key.key_name} \n{ssh_connection.connection_name}")

@app.command()
def init():
    #get all hosts from connections file
    check_if_file_exists(CONNECTIONS_FILE)
    with open(CONNECTIONS_FILE, "r") as file:
        connections = json.load(file)
    hosts = [connection['connection_name']+" - "+connection['connection_user']+" - "+connection['connection_host'] for connection in connections]
    
    if not hosts:
        print("Nenhuma conexão SSH encontrada. \nAdicione uma conexão SSH primeiro - Comando: ssh-manager add-connection")
        return


    #get all keys from keys file
    check_if_file_exists(KEYS_FILE)
    with open(KEYS_FILE, "r") as file:
        keys = json.load(file)
    key_choices = {key['key_name']: key['key_path'] for key in keys}

    if not key_choices:
        print("Nenhuma chave SSH encontrada. \nAdicione uma chave SSH primeiro - Comando: ssh-manager add-key")
        return

    host = questionary.select(
        "Qual host você deseja conectar?",
        hosts, 
    ).ask()

    if host is None:
        print("Cancelado.")
        return

    key_name = questionary.select(
        "Qual chave você deseja usar?",
        list(key_choices.keys()), 
    ).ask()

    if key_name is None:
        print("Cancelado.")
        return

    # Usar o caminho completo da chave
    key_path = os.path.expanduser(key_choices[key_name])
    
    # Extrair nome, usuário e host da string selecionada
    connection_name, user, host = host.split(" - ")
    
    # Gerar comando ssh de conexão com o caminho completo
    ssh_command = f"ssh -i {key_path} {user}@{host}"
    os.system(ssh_command)

if __name__ == "__main__":
    app()