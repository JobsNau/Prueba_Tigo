import requests
import sqlite3 as sql
import csv


def get_names_type():
    url = "https://pokeapi.co/api/v2/type/"
    response = requests.get(url)
    name_type = []

    if response.status_code == 200:
        data = response.json()
        results = data.get('results')

        if results:
            for name in results:
                name_type.append(name['name'])
    return name_type


def nr():
    url = "https://pokeapi.co/api/v2/pokemon/?limit=100"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['count']


def get_names(nr):
    url = f"https://pokeapi.co/api/v2/pokemon/?limit={nr}"
    response = requests.get(url)
    names = []

    if response.status_code == 200:
        data = response.json()
        results = data.get('results')

        if results:
            for name in results:
                names.append(name['name'])
    return names


def get_data(names):
    url = f"https://pokeapi.co/api/v2/pokemon/{names}/"
    data = requests.get(url)

    if data.status_code == 200:
        data = data.json()
        image = data['sprites']['other']['home']['front_default']

        abili = []
        for abilit in data['abilities']:
            abili.append(abilit['ability']['name'])
        ability = abili

        tipe = []
        for typ in data['types']:
            tipe.append(typ['type']['name'])
        types = tipe

        stadist = []
        for sta in data['stats']:
            stadist.append(sta['base_stat'])
        general_statistics = stadist

    return image, ability, general_statistics, types


def createDB(name_BD):
    conn = sql.connect(f"{name_BD}.db")
    conn.commit()
    conn.close()


def createTable(name_BD, name_T):
    conn = sql.connect(f"{name_BD}.db")
    cursor = conn.cursor()
    cursor.execute(f"create table if not exists {name_T} (ID integer primary key, "
                   f"Name varchar (150) unique ,"
                   f"Image text,"
                   f"abili_I varchar (80) ,"
                   f"abili_II varchar (80) ,"
                   f"PS integer ,"
                   f"attack integer ,"
                   f"defense integer ,"
                   f"special_attack integer ,"
                   f"special_defense integer ,"
                   f"speed integer ,"
                   f"Type_I varchar (80) ,"
                   f"Type_II varchar (80) ,"
                   f"Type_III varchar (80))")

    conn.commit()
    conn.close()


def insertRow(name_db, name_T, data):
    conn = sql.connect(f"{name_db}.db")
    cursor = conn.cursor()
    cursor.execute(f"insert into {name_T} values({data[0]},'{data[1]}','{data[2]}','{data[3][0]}','{data[3][1]}'"
                   f",{data[4][0]},{data[4][1]},{data[4][2]},{data[4][3]},{data[4][4]},{data[4][5]}"
                   f",'{data[5][0]}','{data[5][1]}','{data[5][2]}')")
    conn.commit()
    conn.close()


def updateRow(name_bd, name_T, data):
    conn = sql.connect(f"{name_bd}.db")
    cursor = conn.cursor()
    cursor.execute(
        f"update {name_T} set Name='{data[1]}',Image='{data[2]}', abili_I='{data[3][0]}',abili_II='{data[3][1]}',"
        f"PS={data[4][0]}, attack={data[4][1]}, defense={data[4][2]}, special_attack={data[4][3]}, special_defense={data[4][4]},"
        f"speed={data[4][5]},Type_I='{data[5][0]}', Type_II='{data[5][1]}', Type_III='{data[5][2]}' "
        f" where ID ={data[0]}")
    conn.commit()
    conn.close()


def read(name_bd, name_T):
    conn = sql.connect(f"{name_bd}.db")
    cursor = conn.cursor()
    cursor.execute(f"select Name, Type_I, Type_II, Type_III from {name_T}")
    Type_I = cursor.fetchall()
    conn.commit()
    conn.close()
    return Type_I


def types_pokemons(types):
    name_poke = []
    for i in types:
        cont = 0
        for j in range(1, 4):
            if i[j] != "":
                cont += 1
        if cont > 2:
            name_poke.append(i[0])
    return name_poke


def types_repet(name_bd, name_T, name_col):
    conn = sql.connect(f"{name_bd}.db")
    cursor = conn.cursor()
    cursor.execute(f"select  {name_col}, count(*) from {name_T} where {name_col}<>'' group by {name_col}")
    Type = cursor.fetchall()
    conn.commit()
    conn.close()
    return Type


if __name__ == "__main__":

    # creating database name and table name
    name_BBDD = "Pokemon"
    name_T = "Poke"

    # creating the database and table
    createDB(name_BBDD)
    createTable(name_BBDD, name_T)

    # getting pokemon names
    name = get_names(nr())
    name = []

    # obtaining the different data of the pokemons

    for i in range(len(name)):

        imagen, ability, stats, type = get_data(name[i])

        # Checking that there are two fields in the ability of each pokemon
        while len(ability) < 2:
            ability.append("")

        # Checking that there are three fields in the pokemon type
        while len(type) < 3:
            type.append("")

        # false initializing the function to update the BBDD
        update = False

        # Taking the data to enter the BBDD
        save_data = [i + 1, name[i], imagen, ability, stats, type]

        try:
            # Entering the data into the DB
            insertRow(name_BBDD, name_T, save_data)
        except sql.IntegrityError:
            # Activate the update of the data in case they had already been entered
            update = True
        if update:
            # Update existing database
            updateRow(name_BBDD, name_T, save_data)

    #Querying the pokemons that have more than 2 types
    types = read(name_BBDD, name_T)
    pokemons_2 = types_pokemons(types)
    consult_one=[["Pokemon you have more than two types: " + str(len(pokemons_2))],pokemons_2]

    #Performing query of the type that is repeated the most
    columns = ["Type_I", "Type_II", "Type_III"]
    for i in range(len(columns)):
        if i == 0:
            one = types_repet(name_BBDD, name_T, f"{columns[i]}")
            result = dict(one)
        else:
            one = types_repet(name_BBDD, name_T, f"{columns[i]}")
            for j in one:
                result[j[0]] += j[1]

    max_key = max(result, key=result.get)
    consult_two=[[f"The type that is most repeated among the Pokemons is: {max_key}, with {result[max_key]} times"]]


    with open('results.csv','w', newline='') as file:
        writer=csv.writer(file, delimiter=';')
        writer.writerows(consult_one)
        writer.writerows(consult_two)
        file.close()