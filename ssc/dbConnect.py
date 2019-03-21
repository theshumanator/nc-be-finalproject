mport psycopg2

try:
    connection = psycopg2.connect(
        # user = "",
        # password = "",
        # host = "127.0.0.1",
        # port = "5432",
        database="ssc")
    cursor = connection.cursor()

    # Print PostgreSQL Connection properties
    print(connection.get_dsn_parameters(), "\n")
    # Print PostgreSQL version
    cursor.execute("delete from users where user_id=1;")
    connection.commit()
    count = cursor.rowcount
    print(count, "Record deleted successfully ")

    # print("You are connected to - ", record,"\n")
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    # closing database connection.
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")