export function convertDecimalTimeToHuman(time: number): string {
    const hours = Math.trunc(time)
    const minutes = Math.round((time - hours) * 60)
    return `${hours}:${toStringAtLeastTwoDigits(minutes)}`
}

/**
 * Takes a number and convert it to a string with a '0' prefix if there is only one digit.
 * If the number is in a string then a '0' prefix is prepended if needed.
 * @param {number} element The element to convert
 * @returns {string} The two-digits string
 */
export function toStringAtLeastTwoDigits(element: number | string) {
    if (typeof element === 'string') {
        element = parseInt(element, 10)
        if (isNaN(element)) {
            throw new Error(`Given value (${element}) cannot not be parsed as number`)
        }
    }
    return `${element < 10 ? `0${element}` : element}`
}

export function parseReason(reason: unknown, onAlert?: (level: string, message: string) => void) {
    // Reason can be either a response body or a thrown error
    if (reason instanceof Object && !(reason instanceof Error)) {
        // Reason is a response body, display each message separately
        const reasonObj = reason as { [key: string]: string }
        Object.keys(reasonObj).forEach((key) => {
            onAlert?.('danger', `${key}: ${reasonObj[key]}`)
        })
    } else {
        onAlert?.('danger', `${reason}. Please contact an administrator.`)
    }
}

/**
 * Takes an array and a predicate to extract a key serving as the group-by option.
 * Returns an object having each key property matching a list of given type.
 * @param list The array
 * @param keyPredicate The function to extract a key from each element
 */
export function listGroupBy<T>(list: Array<T>, keyPredicate: (value: T) => string): { [p: string]: Array<T> } {
    const out: { [day: string]: Array<T> } = {}
    list.forEach((value) => {
        const key = keyPredicate(value)
        if (!(key in out)) {
            out[key] = []
        }
        out[key].push(value)
    })
    return out
}
