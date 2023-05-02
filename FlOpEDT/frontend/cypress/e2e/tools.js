const URL = "http://localhost:8000/fr/edt/INFO/"
const ID = "MOI"
const PASSWORD = "passe"

export function connect() {
    cy.visit(URL)
    cy.get('#sign_in').click()
    cy.get('#id_username').type(ID)
    cy.get('#id_password').type(PASSWORD)
    cy.get('input[type="submit"]').click()
}
