from neo4j import GraphDatabase

# 1. Define Connection Details (using the current/expired password)
URI = "neo4j://localhost:7687"
USER = "neo4j"
EXPIRED_PASSWORD = "neo4j"  # The password you used that triggered the error
NEW_PASSWORD = "MySecureNewPassword123" # <-- CHOOSE YOUR NEW SECURE PASSWORD!

# 2. Establish the Driver Connection
driver = GraphDatabase.driver(URI, auth=(USER, EXPIRED_PASSWORD))

# 3. Define the Password Change Query Function
def change_password(tx, new_pass):
    # The Cypher statement to change the password
    query = f"ALTER CURRENT USER SET PASSWORD FROM '{EXPIRED_PASSWORD}' TO '{new_pass}'"
    tx.run(query)
    print("✅ Password change query executed successfully.")
    
# 4. Execute the Password Change
try:
    # A session connecting to the 'system' database is required for password changes.
    with driver.session(database="system") as session:
        # Use execute_write to run the transaction
        session.execute_write(change_password, NEW_PASSWORD)

except Exception as e:
    # You should not see an error here if the old password was correct
    print(f"An error occurred during password change: {e}")

finally:
    # 5. Close the Driver
    driver.close()

# --------------------------------------------------------------------------------
# After running the script once, the password will be changed.
# You can now test the connection with the NEW_PASSWORD.
# --------------------------------------------------------------------------------

print("\n--- Testing new connection with the new password ---")

# 6. Test the New Connection
try:
    test_driver = GraphDatabase.driver(URI, auth=(USER, NEW_PASSWORD))
    
    with test_driver.session() as session:
        # Run a simple query on the default 'neo4j' database
        greeting = session.execute_read(lambda tx: tx.run("RETURN 'Connection Successful!' AS message").single()[0])
        print(f"Server response: {greeting}")
        
except Exception as e:
    print(f"An error occurred during connection test: {e}")
    
finally:
    test_driver.close()