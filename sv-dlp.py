import os
import typer
from extractor import *

app = typer.Typer()

def add_services(folder):
    service_arr = os.listdir(folder)
    for i in range(len(service_arr) -1):
        if service_arr[i][-3:] != '.py':
            service_arr.pop(i)
    return service_arr

@app.command()
def hello(
    name: str):

    typer.echo(f"Hello {name}")

@app.command()
def goodbye(
    name: str, 
    formal: bool = False):
    
    if formal:
        typer.echo(f"Goodbye Ms. {name}. Have a good day.")
    else:
        typer.echo(f"Bye {name}!")


if __name__ == "__main__":
    services = add_services('extractor')
    print(google.is_trekker("jYxwHUdPuhm8NGfAH6y8IA"))