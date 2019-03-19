import psycopg2

from ssc.Utils.db_ops import get_workspace_id, get_user_id, is_user_admin
from ssc.dbconfig import user, password, database

def delete_workspace(delete_request):
    deleted_by = delete_request['deleted_by']
    workspace = delete_request['workspace']
    workspace_id = get_workspace_id(workspace)
    deleted_by_id = get_user_id(deleted_by)
    if (workspace_id == -1 | deleted_by_id == -1):
        return False

    try:
        connection = psycopg2.connect(
            user=user,
            password=password,
            database=database)
        cursor = connection.cursor()

        admin_status = is_user_admin(deleted_by_id, workspace_id)

        if (admin_status == 0):
            return False

        delete_workspace_sql = "delete from workspaces where workspace_id=%s"
        cursor.execute(delete_workspace_sql, (workspace_id,))
        connection.commit()
        count = cursor.rowcount

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return False

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    if (count == 0): return False
    return True


def update_admin(workspace, admin_request):
    username = admin_request['username']
    admin_username = admin_request['admin_username']
    make_admin = admin_request['make_admin']

    workspace_id = get_workspace_id(workspace)
    user_id = get_user_id(username)
    admin_id = get_user_id(admin_username)

    if (workspace_id == -1 | admin_id == -1 | user_id == -1):
        return False

    try:
        connection = psycopg2.connect(
            user=user,
            password=password,
            database=database)
        cursor = connection.cursor()

        admin_status = is_user_admin(admin_id, workspace_id)

        if (admin_status == 0):
            return False

        if (make_admin == 'True'):
            make_admin_bool = True;
        else:
            make_admin_bool = False;

        update_admin_sql = "update workspace_users set is_admin=%s where workspace_id=%s" \
                           "and user_id=%s"
        cursor.execute(update_admin_sql, (make_admin_bool, workspace_id, user_id))
        connection.commit()
        count = cursor.rowcount

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return False

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    if (count == 0): return False
    return True


def create_workspace_only(data):
    try:
        workspace_name = data['name']
        admin = data['admin'];
        admin_id = get_user_id(admin)

        connection = psycopg2.connect(
            user=user,
            password=password,
            database=database)

        insert_workspace_name = "insert into workspaces (name) values (%s) returning workspace_id"

        cursor = connection.cursor()
        cursor.execute(insert_workspace_name, (workspace_name,))
        connection.commit()
        count = cursor.rowcount
        if (count == 0):
            return False;

        new_workspace_id = cursor.fetchone()[0]

        add_user_to_workspace([admin_id], new_workspace_id, True)

    except (Exception, psycopg2.Error) as error:
        print('Error while conecting to PostgresQL', error)
        return False
    finally:

        if (connection):
            # close the connection and the cursor
            cursor.close()
            connection.close()
            print("PostgresSQL connection is closed")

    return True


def create_workspace_with_users(data):
    users = data['users'];
    admin = data['admin'];
    workspace = data['name'];

    try:
        connection = psycopg2.connect(
            database=database)

        cursor = connection.cursor()

        insert_workspace_sql = "insert into workspaces (name) values (%s) " \
                               "returning workspace_id"
        cursor.execute(insert_workspace_sql, (workspace,))
        connection.commit()

        count = cursor.rowcount
        if (count == 0):
            return count;

        new_workspace_id = cursor.fetchone()[0]
        admin_id = get_user_id(admin)
        admin_added = add_user_to_workspace([admin_id], new_workspace_id, True);
        if (admin_added == 0):
            return admin_added;

        user_id_list = []
        for user in users:
            user_id_list.append(get_user_id(user['username']))

        users_added = add_user_to_workspace(user_id_list, new_workspace_id);
    except (Exception, psycopg2.Error) as error:
        print('Error while conecting to PostgresQL', error)
        return 0
    finally:
        if (connection):
            # close the connection and the cursor
            cursor.close()
            connection.close()
            print("PostgresSQL connection is closed")

    return users_added;


def add_user_to_workspace(list_of_ids, workspace_id, is_admin=False):
    try:
        connection = psycopg2.connect(
            user=user,
            password=password,
            database=database)

        cursor = connection.cursor()
        insert_user_to_workspace_sql = "insert into workspace_users (user_id, workspace_id, is_admin) " \
                                       "values (%s,%s,%s) returning user_id"

        count = 0
        for user_id in list_of_ids:
            if (user_id!=-1):
                cursor.execute(insert_user_to_workspace_sql, (user_id, workspace_id, is_admin))
                connection.commit()
                count += cursor.rowcount

    except (Exception, psycopg2.Error) as error:
        print('Error while conecting to PostgresQL', error)
        return 0
    finally:
        if (connection):
            # close the connection and the cursor
            cursor.close()
            connection.close()
            print("PostgresSQL connection is closed")

    return count