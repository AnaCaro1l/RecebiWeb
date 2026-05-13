from app import create_app

app = create_app()

if __name__ == '__main__':
    # O debug=True faz com que o servidor reinicie sozinho toda vez que você salvar o código
    app.run(debug=True, port=5000)