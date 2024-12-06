import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


class DatabaseManager:
    def __init__(self, database_name):
        self.database_name = database_name

    def create_connection(self):
        try:
            conn = sqlite3.connect(self.database_name)
            return conn
        except sqlite3.Error as e:
            print(F"Error connecting to database:: {e}")
            return None

    def create_tables(self):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_info(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
        );""")

        cursor.execute("""
        
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                task_description TEXT NOT NULL,
                user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users (id)
        );""")

        conn.commit()
        conn.close()

    def add_user(self, username, password):
        """Add a new user with hashed password"""
        hashed_password = generate_password_hash(password)
        sql = """
        INSERT INTO user_info (username, password)
        VALUES(?, ?);
        """

        try:
            with self.create_connection() as conn:
                conn.execute(sql, (username, hashed_password))
                conn.commit()
                print("User added")
                return True
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
            return False

    def add_task(self, task_name, task_description, user_id):
        sql = """
        INSERT INTO tasks (task_name, task_description, user_id)
        VALUES (?, ?, ?);
        """

        print(f"Inserting task: {task_name}, {task_description}, {user_id}")  #for Debugging

        try:
            with self.create_connection() as conn:
                conn.execute(sql, (task_name, task_description, user_id))
                conn.commit()
                print("Task added successfully!")
                return True
        except sqlite3.Error as e:
            print(f"Error adding task: {e}")
            return False

    def verify_user(self, username, password):
        """Verify user credentials"""
        sql = "SELECT password FROM user_info WHERE username = ?;"
        try:
            with self.create_connection() as conn:
                cursor = conn.execute(sql, (username,))
                result = cursor.fetchone()
                if result and check_password_hash(result[0], password):
                    return True
                return False
        except sqlite3.Error as e:
            print(f"Error verifying user: {e}")
            return False

    def user_exists(self, username):
        """Check if username already exists"""
        sql = "SELECT 1 FROM user_info WHERE username = ?;"
        try:
            with self.create_connection() as conn:
                cursor = conn.execute(sql, (username,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Error checking user existence: {e}")
            return False

    def get_all_users(self):
        sql = "SELECT id, username FROM user_info;"  # Note: not returning passwords
        try:
            with self.create_connection() as conn:
                cursor = conn.execute(sql)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving users: {e}")
            return []

    def get_user_by_username(self, username):
        sql = "SELECT id FROM user_info WHERE username = ?;"  # Note: not returning passwords
        try:
            with self.create_connection() as conn:
                cursor = conn.execute(sql, (username,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error retrieving users: {e}")
            return []

    def get_tasks_for_user(self, user_id):


        sql = "SELECT id, task_name, task_description FROM tasks WHERE user_id = ?"
        try:
            with self.create_connection() as conn:
                cursor = conn.execute(sql, (user_id,))
                tasks = cursor.fetchall()  # Get all tasks for the given user_id
                print(f"Tasks for user {user_id}: {tasks}")  # Debugging
                return tasks
        except sqlite3.Error as e:
            print(f"Error retrieving tasks: {e}")
            return []


    def get_task_by_id(self, task_id):
        """Retrieve a task by its ID"""
        sql = "SELECT id, task_name, task_description FROM tasks WHERE id = ?;"
        try:
            with self.create_connection() as conn:
                cursor = conn.execute(sql, (task_id,))
                task = cursor.fetchone()  # This will return a tuple (id, task_name, task_description)
                return task
        except sqlite3.Error as e:
            print(f"Error retrieving task by ID: {e}")
            return None

    def update_task(self, task_id, task_name, task_description):
        sql = """
        UPDATE tasks
        SET task_name = ?, task_description = ?
        WHERE id = ?;
        """
        try:
            with self.create_connection() as conn:
                conn.execute(sql, (task_name, task_description, task_id))
                conn.commit()
                print("Task updated successfully!")
                return True
        except sqlite3.Error as e:
            print(f"Error updating task: {e}")
        return False

    def delete_task(self, task_id):
        sql = "DELETE FROM tasks WHERE id = ?;"
        try:
            with self.create_connection() as conn:
                conn.execute(sql, (task_id,))
                conn.commit()
                print("Task deleted successfully!")
                return True
        except sqlite3.Error as e:
            print(f"Error deleting task: {e}")
            return False


if __name__ == "__main__":
    # Test the enhanced functionality
    db = DatabaseManager("database.db")
    db.create_tables()

    # Test user creation with hashed password
    db.add_user("testuser", "testpass")

    # Test verification
    print("Verification test:")
    print("Correct password:", db.verify_user("testuser", "testpass"))
    print("Wrong password:", db.verify_user("testuser", "wrongpass"))

    # Test user existence
    print("\nUser existence test:")
    print("testuser exists:", db.user_exists("testuser"))
    print("nonexistent exists:", db.user_exists("nonexistent"))