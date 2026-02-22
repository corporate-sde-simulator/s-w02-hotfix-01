"""
====================================================================
 JIRA: SVC-1850 — Fix SQL Injection in User Search
====================================================================
 Priority: P0 — Security | Sprint: Sprint 24 | Points: 2
 Reporter: Security Team (Code Scan)
 Labels: security, database, python
 
 DESCRIPTION:
 User search endpoint constructs SQL using string formatting instead
 of parameterized queries. An attacker can inject SQL via the search
 field to dump the entire user table.
 
 SECURITY SCAN OUTPUT:
 [CRITICAL] SQL injection at line 25: f"SELECT * FROM users WHERE name LIKE '%{query}%'"
 [CRITICAL] No input sanitization on 'query' parameter
 
 SLACK — #security:
 @security-lead: "Code scan found SQL injection in searchUsers. String
   concat'd directly into query. Use parameterized queries."
 @lead: "@intern — Fix it. Use cursor.execute(sql, params) pattern."

 ACCEPTANCE CRITERIA:
 - [ ] All SQL queries use parameterized syntax (? or %s placeholders)
 - [ ] No string concatenation or f-strings in SQL construction
 - [ ] Input validation on query length (max 100 chars)
 - [ ] Test with payload: ' OR 1=1 -- should return no results
====================================================================
"""

import sqlite3

class UserRepository:
    def __init__(self, db_path=':memory:'):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            department TEXT,
            active INTEGER DEFAULT 1
        )''')
        self.conn.commit()

    def search_users(self, query):
        """Search users by name."""
        # BUG: SQL Injection vulnerability — string concatenation in SQL
        # An attacker sending query = "' OR '1'='1" gets all users
        sql = f"SELECT * FROM users WHERE name LIKE '%{query}%'"
        cursor = self.conn.execute(sql)
        return cursor.fetchall()

    def get_user_by_id(self, user_id):
        # BUG: Same pattern — string formatting instead of parameterized query
        sql = f"SELECT * FROM users WHERE id = {user_id}"
        cursor = self.conn.execute(sql)
        return cursor.fetchone()

    def update_user_status(self, user_id, active):
        # BUG: Again, string formatting
        sql = f"UPDATE users SET active = {active} WHERE id = {user_id}"
        self.conn.execute(sql)
        self.conn.commit()

    def add_user(self, name, email, department):
        # This one is correct — uses parameterized query
        self.conn.execute(
            "INSERT INTO users (name, email, department) VALUES (?, ?, ?)",
            (name, email, department)
        )
        self.conn.commit()


# ─── Tests ──────────────────────────────────────
if __name__ == '__main__':
    repo = UserRepository()
    repo.add_user("Alice Smith", "alice@corp.com", "Engineering")
    repo.add_user("Bob Jones", "bob@corp.com", "Marketing")

    # Normal search should work
    results = repo.search_users("Alice")
    assert len(results) == 1, f"FAIL: Expected 1 result for 'Alice', got {len(results)}"

    # SQL injection should NOT return all users
    injection = repo.search_users("' OR '1'='1")
    assert len(injection) == 0, f"FAIL: SQL injection returned {len(injection)} users!"

    print("All tests passed!")
