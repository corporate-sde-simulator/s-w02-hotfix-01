# Beginner Explanatory Guide: SVC-1850: Fix SQL Injection in User Search

> **Task Type**: Service Task  
> **Domain/Focus**: Database queries, Python fundamentals

---

## 1. The Goal (In-Depth Beginner Explanation)

### The Core Problem
The task at hand addresses a critical security vulnerability in the `UserRepository` class, specifically within the `search_users`, `get_user_by_id`, and `update_user_status` methods. Currently, these methods construct SQL queries using string formatting, which allows for SQL injection attacks. SQL injection is a technique where an attacker can manipulate a query by injecting malicious SQL code through user input. For instance, if a user inputs a query like `"' OR '1'='1"`, the SQL command would be altered to return all users instead of filtering by name. This not only compromises the integrity of the database but also poses a significant risk to user data privacy and security.

Fixing this issue is paramount because it protects the application from unauthorized access and data breaches. In a production environment, such vulnerabilities can lead to severe consequences, including data loss, legal repercussions, and damage to the organization's reputation. By implementing parameterized queries, we can ensure that user input is treated as data rather than executable code, thus safeguarding the application against these types of attacks.

### Jargon Buster (Key Terms Explained)
* **SQL Injection**: A type of attack where an attacker inserts or "injects" malicious SQL code into a query. For example, if a search input is not properly sanitized, an attacker could input `"' OR '1'='1"` to bypass authentication and retrieve all records from a database.
  
* **Parameterized Queries**: A method of constructing SQL queries that separates the SQL code from the data. Instead of embedding user input directly into the SQL string, placeholders (like `?` or `%s`) are used, and the actual values are provided separately. This prevents SQL injection by ensuring that user input is treated as data only.

* **Input Validation**: The process of checking user input to ensure it meets certain criteria before processing it. For instance, validating that a search query does not exceed a certain length (e.g., 100 characters) helps prevent malicious input.

* **Cursor**: An object used to interact with the database. It allows you to execute SQL commands and fetch results. In Python's SQLite library, a cursor is created from a connection object and is used to execute queries and retrieve data.

### Expected Outcome
After implementing the necessary fixes, the system should behave as follows:

**Before**: 
- The `search_users` method allows SQL injection, potentially returning all users when malicious input is provided.
- The `get_user_by_id` and `update_user_status` methods also expose the application to similar vulnerabilities.

**After**: 
- All SQL queries in the `UserRepository` class use parameterized syntax, preventing SQL injection.
- Input validation ensures that user queries are limited to a maximum length of 100 characters, rejecting overly long or suspicious inputs.
- The application is secure against unauthorized data access, and user data integrity is maintained.

---

## 2. Related Coding Concepts & Syntax (50% Theory, 50% Practice)

### Concept 1: Parameterized Queries
#### 📘 Theoretical Overview (50%)
* **Why it exists**: Parameterized queries are essential for preventing SQL injection attacks. When user input is directly concatenated into SQL strings, it can be manipulated to execute unintended commands. By using parameterized queries, we ensure that user input is treated strictly as data, thus mitigating the risk of injection.

* **Key Mechanisms**: In a parameterized query, placeholders are used in the SQL statement. When the query is executed, the database engine safely substitutes the placeholders with the actual values. This separation of code and data prevents attackers from altering the SQL command structure.

#### 💻 Syntax & Practical Examples (50%)
* **Language Syntax**:
  ```python
  cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))
  ```
  - `cursor.execute`: This method executes the SQL command.
  - `"SELECT * FROM users WHERE name = ?"`: The `?` is a placeholder for the user input.
  - `(user_input,)`: A tuple containing the actual value to be substituted into the placeholder.

* **Real-World Application**:
  ```python
  def search_users(self, query):
      """Search users by name using a parameterized query."""
      if len(query) > 100:
          raise ValueError("Query exceeds maximum length of 100 characters.")
      sql = "SELECT * FROM users WHERE name LIKE ?"
      cursor = self.conn.execute(sql, ('%' + query + '%',))
      return cursor.fetchall()
  ```
  - This example demonstrates how to safely search for users by name while validating the input length.

---

## 3. Step-by-Step Logic & Walkthrough

1. **Step 1: Locate and Analyze the Target File**
   * Open the folder `s-w02-hotfix-01` and locate the file `userRepository.py`.
   * Focus on the methods: `search_users`, `get_user_by_id`, and `update_user_status`. These methods contain the SQL queries that need to be fixed.

2. **Step 2: Input Verification & Validation**
   * In the `search_users` method, check if the `query` parameter is longer than 100 characters. If it is, raise a `ValueError` to prevent processing invalid input.

3. **Step 3: Core Implementation / Modification**
   * Modify the SQL queries in the identified methods to use parameterized syntax. For example:
     - Change `sql = f"SELECT * FROM users WHERE name LIKE '%{query}%'"` to `sql = "SELECT * FROM users WHERE name LIKE ?"` and pass the parameters as a tuple.
   * Ensure similar changes are made in `get_user_by_id` and `update_user_status`.

4. **Step 4: Output Verification & Testing**
   * At the bottom of the `userRepository.py` file, run the tests to verify that the changes work as expected. Check for any errors or unexpected behavior.

---

## 4. Detailed Walkthrough of Test Cases

### Test Case 1: Standard / Success Case
* **Description**: This test checks if the `search_users` method correctly retrieves users when a valid query is provided.
* **Inputs**:
  ```json
  {
    "query": "Alice"
  }
  ```
* **Step-by-Step Execution Trace**:
  1. The input value `"Alice"` is received by the `search_users` method.
  2. The method checks the length of the query, which is valid (5 characters).
  3. The SQL command is executed with the parameterized query, safely substituting the input.
  4. Returns the user records matching the name "Alice".
* **Expected Output**: A list of user records that match the name "Alice".

### Test Case 2: Edge Case / Validation Fail
* **Description**: This test checks the behavior of the `search_users` method when an overly long query is provided.
* **Inputs**:
  ```json
  {
    "query": "A" * 101  // 101 characters long
  }
  ```
* **Step-by-Step Execution Trace**:
  1. The input value (101 characters) is received by the `search_users` method.
  2. The method checks the length of the query, which exceeds the maximum allowed length.
  3. A `ValueError` is raised with the message "Query exceeds maximum length of 100 characters."
  4. The execution is halted, and no SQL command is executed.
* **Expected Output**: A `ValueError` exception indicating that the input is invalid.