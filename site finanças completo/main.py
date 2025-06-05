from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)

usuarios = {}
transacoes = []

app.secret_key = "Adoro batatas fritas como molho especial e um x-tudo como um garaná paulistinha"

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["Nome"]
        cpf = request.form["CPF"]
        telefone = request.form["Telefone"]
        email = request.form["email"]
        senha = request.form["senha"]
        confirmar_senha = request.form["confirmar_senha"]

        if cpf in usuarios:
            flash("Cpf ou Email já cadastrados")
            return render_template("cadastro.html")

        for u in usuarios.values():
            if u["email"] == email:
                flash("Cpf ou Email já cadastrados")
                return render_template("cadastro.html")

        if senha != confirmar_senha:
            flash("As senhas não coincidem")
            return render_template("cadastro.html")

        maiusculo = minuscula = numero = caracterEspecial = False
        for s in senha:
            if s.isupper():
                maiusculo = True
            elif s.islower():
                minuscula = True
            elif s.isdigit():
                numero = True
            elif not s.isalnum():
                caracterEspecial = True

        if not (maiusculo and minuscula and numero and caracterEspecial):
            flash("Sua senha deve ter uma Letra maiuscula, uma letra minuscula, um caractere especial e um numero")
            return render_template("cadastro.html")
            

        if len(senha) < 8:
            flash("Sua senha deve ter pelo menos 8 caracteres!")
            return render_template("cadastro.html")
        
        session["usuario_nome"] = nome
        session["usuario_cpf"] = cpf

        usuarios[cpf] = {
            "CPF": cpf,
            "Nome": nome,
            "Telefone": telefone,
            "email": email,
            "senha": senha
        }


        return redirect(url_for("cadastro_adicionado", cpf=cpf))
    return render_template("cadastro.html")


@app.route("/cadastro_adicionado/<cpf>")
def cadastro_adicionado(cpf):
    usuario = usuarios[cpf]
    session["usuario_nome"] = usuario["Nome"]
    session["usuario_cpf"] = cpf
    return render_template("cadastro_adicionado.html", usuario=usuario)
    

@app.route("/editar/<cpf>", methods=["GET", "POST"])
def editar_cadastro(cpf):
    usuario = usuarios.get(cpf)
    if request.method == "POST":
        nome = request.form["Nome"]
        telefone = request.form["Telefone"]
        email = request.form["email"]
        senha = request.form["senha"]

        for outro_cpf, outro_usuario in usuarios.items():
            if outro_cpf != cpf and outro_usuario["email"] == email:
                flash("Este e-mail já está cadastrado por outro usuário.")
                return render_template("editar_cadastro.html", usuario=usuario, cpf=cpf)


        
        maiusculo = minuscula = numero = caracterEspecial = False
        for s in senha:
            if s.isupper():
                maiusculo = True
            elif s.islower():
                minuscula = True
            elif s.isdigit():
                numero = True
            elif not s.isalnum():
                caracterEspecial = True

        if not (maiusculo and minuscula and numero and caracterEspecial):
            flash("A senha deve conter uma letra maiúscula, uma minúscula, um número e um caractere especial.")
            return render_template("editar_cadastro.html", usuario=usuario, cpf=cpf)

        if len(senha) < 8:
            flash("A senha deve ter pelo menos 8 caracteres.")
            return render_template("editar_cadastro.html", usuario=usuario, cpf=cpf)

   
        usuario["Nome"] = nome
        usuario["Telefone"] = telefone
        usuario["email"] = email
        usuario["senha"] = senha

        session["usuario_nome"] = nome
        return redirect(url_for("cadastro_adicionado", cpf=cpf))

    return render_template("editar_cadastro.html", usuario=usuario, cpf=cpf)

@app.route("/login",methods =["GET","POST"] )
def login():
    erro = None
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        for cpf, usuario in usuarios.items():
            if usuario["email"] == email and usuario["senha"] == senha:
                session["usuario_nome"] = usuario["Nome"]
                session["usuario_cpf"] = cpf
                return redirect(url_for("index", cpf=cpf))
        erro = "E-mail ou senha incorretos. Por favor, tente novamente."
    return render_template("login.html", erro=erro)

@app.route("/logout")
def logout():
    session.pop("usuario_nome", None)
    return redirect(url_for("index"))

@app.route("/transacoes")
def registro_transacoes():
    cpf = session.get("usuario_cpf")
    transacoes_usuario = [t for t in transacoes if t["cpf"] == cpf]
    saldo = 0
    for t in transacoes_usuario:
        if t["tipo"] == "Receita":
            saldo += t["valor"]
        elif t["tipo"] == "Despesa":
            saldo -= t["valor"]

    saldo = round(saldo, 2)

    return render_template("registro_transacoes.html", transacoes=transacoes_usuario, saldo=saldo)


@app.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        tipo = request.form["tipo"]
        Nome = request.form["Nome"]
        data = request.form["data"]
        valor = float(request.form["valor"])
        cpf = session.get("usuario_cpf")
        datagringa = datetime.strptime(data,"%Y-%m-%d")
        databrasil = datagringa.strftime("%d/%m/%Y")

        if valor <= 0:
            flash("O valor deve ser maior que zero.")
            return redirect(url_for("nova"))


        transacoes.append({
            "cpf": cpf,
            "tipo": tipo,
            "data": databrasil,
            "Nome": Nome,
            "valor": valor,
            "dataeditar": data
        })

        return redirect(url_for("registro_transacoes"))

    return render_template("nova.html")


@app.route("/deletar_transacao", methods=["POST"])
def deletar_transacao():
    cpf = session.get("usuario_cpf")

    nome = request.form["nome"]
    valor = float(request.form["valor"])
    data = request.form["data"]
    
    transacao_para_remover = None
    for transacao in transacoes:
        if (
            transacao["cpf"] == cpf and
            transacao["Nome"] == nome
            and transacao["valor"] == valor
            and transacao["data"] == data
        ):
            transacao_para_remover = transacao
            break
    
    if transacao_para_remover:
        transacoes.remove(transacao_para_remover)
    
    return redirect(url_for("registro_transacoes"))

@app.route("/editar_transacao", methods=["POST"])
def editar_transacao():
    cpf = session.get("usuario_cpf")
    nome = request.form["nome"]
    valor = float(request.form["valor"])
    data = request.form["data"]

    if valor <= 0:
            flash("O valor deve ser maior que zero.")
            return redirect(url_for("editar_transacao"))


    datagringa = datetime.strptime(data, "%Y-%m-%d")
    data_formatada = datagringa.strftime("%d/%m/%Y")

    for transacao in transacoes:
        if (
            transacao["cpf"] == cpf and
            transacao["Nome"] == nome and
            transacao["valor"] == valor and
            transacao["data"] == data_formatada
        ):
            return render_template("editar_transacao.html", transacao=transacao)

    return redirect(url_for("registro_transacoes"))

@app.route("/atualizar_transacao", methods=["POST"])
def atualizar_transacao():
    cpf = session.get("usuario_cpf")

    nome_original = request.form["nome_original"]
    valor_original = float(request.form["valor_original"])
    data_original = request.form["data_original"]
    tipo_original = request.form["tipo_original"]

    nome_novo = request.form["nome"]
    valor_novo = float(request.form["valor"])
    data_nova = request.form["data"]
    tipo_novo = request.form["tipo"]

    data_nova_formatada = datetime.strptime(data_nova, "%Y-%m-%d").strftime("%d/%m/%Y")

    for transacao in transacoes:
        if (
            transacao["cpf"] == cpf and
            transacao["Nome"] == nome_original and
            transacao["valor"] == valor_original and
            transacao["data"] == data_original and
            transacao["tipo"] == tipo_original
        ):
            transacao["Nome"] = nome_novo
            transacao["valor"] = valor_novo
            transacao["data"] = data_nova_formatada
            transacao["dataeditar"] = data_nova 
            transacao["tipo"] = tipo_novo
            break

    return redirect(url_for("registro_transacoes"))


@app.route("/reserva_emergencia", methods=["POST", "GET"])
def reserva_emergencia():
 
    if request.method == "POST":
        try:
            despesa = float(request.form["despesa"])
            cobertura = int(request.form["cobertura"])
            prazometa = int(request.form["prazometa"])
 
            if despesa <= 0:
                flash("A despesa deve ser maior que zero.")
                return redirect(url_for("reserva_emergencia"))
            elif cobertura <= 0:
                flash("A cobertura deve ser maior que zero.")
                return redirect(url_for("reserva_emergencia"))
            elif prazometa <= 0:
                flash("O prazo da meta deve ser maior que zero.")
                return redirect(url_for("reserva_emergencia"))
            else:
                reservatotal = despesa * cobertura
                reservamensal = reservatotal / prazometa
 
                return render_template(
                    "resultado_reserva.html",
                    despesa=despesa,
                    cobertura=cobertura,
                    prazometa=prazometa,
                    reservatotal=reservatotal,
                    reservamensal=reservamensal
                )
        except ValueError:
            flash("Por favor, insira o valores numéricos válidos.")
        return redirect(url_for("reserva_emergencia"))
    return render_template("reserva_emergencia.html")
 



if __name__ == '__main__':
    app.run(debug=True)