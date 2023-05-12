/**
 * @class
 */
export class Week {
    private _id!: number
    private _nb!: number
    private _year!: number

    constructor(id: number, nb: number, year: number) {
        this.id = id
        this.nb = nb
        this.year = year
    }

    get id() {
        return this._id
    }
    set id(id) {
        this._id = id
    }

    get nb() {
        return this._nb
    }
    set nb(nb) {
        this._nb = nb
    }

    get year() {
        return this._year
    }
    set year(year) {
        this._year = year
    }

    toString() {
        return this.nb + "/" + this.year
    }

    static serialize(week: Week) {
        throw Error('Method not yet implemented')
    }

    static unserialize(obj: any) {
        return new Week(obj.id, obj.nb, obj.year)
    }
}
