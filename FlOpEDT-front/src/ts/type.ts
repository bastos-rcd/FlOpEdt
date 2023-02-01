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