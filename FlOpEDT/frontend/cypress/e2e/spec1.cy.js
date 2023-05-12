import {connect} from './tools.js'
const CSTMANAGER_URL = 'http://localhost:8000/fr/cstmanager/manager/'

export function goToCstManagerPage() {
    connect()
    cy.visit(CSTMANAGER_URL)
}

describe('Make sure our todo list app is working well', () => {
    //1
    // it('Test that we can open connect and go to the right page', () => {
    //     goToCstManagerPage()
    // }) 

    it('Test that we can open a browser and load our app', () => {
        goToCstManagerPage()
        cy.wait(5000)
        cy.get('#popover-MinTutorsHalfDays1').rightclick()

    }) 

    //popover-MinTutorsHalfDays1
})