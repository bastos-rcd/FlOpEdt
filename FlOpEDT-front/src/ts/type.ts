export interface User {
    username: string,
    first_name: string,
    last_name: string,
    email: string,
    id: number,
}

export class User implements User {
    username = ''
    first_name = ''
    last_name = 'AnonymousUser'
    email = ''
    id = -1
}

export interface Department {
    id: number
    abbrev: string
}

export class Department implements Department{
    id = -1
    abbrev = "Not found"

    constructor(id: number, abbrev: string) {
        this.id = id
        this.abbrev = abbrev
    }
}