from keycloak import KeycloakAdmin

admin = KeycloakAdmin(
    server_url="http://localhost:8080/",
    username="admin",
    password="password",
    realm_name="master",
)
user_id = admin.get_user_id("test_user")
admin.delete_user(user_id)