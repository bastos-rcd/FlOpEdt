let API_ENDPOINT = ''

const dbDataElement = document.getElementById('json_data')
if (dbDataElement && dbDataElement.textContent) {
    const data = JSON.parse(dbDataElement.textContent)
    if ('api' in data) {
        API_ENDPOINT = data.api
    }
}

function getCookie(name: string) {
    if (!document.cookie) {
        return null
    }

    const xsrfCookies = document.cookie
        .split(';')
        .map((c) => c.trim())
        .filter((c) => c.startsWith(name + '='))

    if (xsrfCookies.length === 0) {
        return null
    }
    return decodeURIComponent(xsrfCookies[0].split('=')[1])
}

const csrfToken = getCookie('csrftoken')

function createRequestHeader(method: string): RequestInit {
    // Setup headers
    const requestHeaders: HeadersInit = new Headers()
    requestHeaders.set('Content-Type', 'application/json')

    if (csrfToken) {
        requestHeaders.set('X-CSRFToken', csrfToken)
    }

    // Setup request
    return {
        method: method,
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: requestHeaders,
        redirect: 'follow',
        referrerPolicy: 'same-origin',
    }
}

async function doFetch(url: string, requestInit: RequestInit) {
    return await fetch(url, requestInit)
        .then(async (response) => {
            const data = await response.json()
            if (!response.ok) {
                const error = data || `Error ${response.status}: ${response.statusText}`
                return Promise.reject(error)
            }
            return data
        })
        .catch((reason) => {
            return Promise.reject(reason)
        })
}

export async function useFetch<T>(url: string, filters: Partial<T>) {
    const requestInit = createRequestHeader('GET')

    let args = ''

    if (filters) {
        type ObjectKey = keyof typeof filters

        args = Object.keys(filters)
            .map((p) => p + '=' + filters[p as ObjectKey])
            .join('&')
    }
    const finalUrl = `${API_ENDPOINT}${url}/?${args}`
    console.log(`Fetching ${finalUrl}...`)

    return doFetch(finalUrl, requestInit)
}

async function sendData<T>(method: string, url: string, optional: { data?: T; id?: number }): Promise<T | never> {
    if (!['PUT', 'POST', 'DELETE', 'PATCH'].includes(method)) {
        return Promise.reject('Method must be either PUT, POST, PATCH, or DELETE')
    }

    const requestInit = createRequestHeader(method)

    if (optional.data) {
        requestInit.body = JSON.stringify(optional.data)
    }

    // Create url
    let endUrl = '/'
    if (optional.id) {
        endUrl = `/${optional.id}/`
    }
    const finalUrl = `${API_ENDPOINT}${url}${endUrl}`

    console.log(`Updating ${finalUrl}...`)

    // Return the resulting fetch
    return doFetch(finalUrl, requestInit)
}

export function usePut<T>(url: string, id: number, data: T): Promise<T | never> {
    const optional: { [key: string]: unknown } = {
        id: id,
        data: data,
    }
    return sendData('PUT', url, optional)
}

export function usePost<T>(url: string, data: T): Promise<T | never> {
    const optional: { [key: string]: unknown } = {
        data: data,
    }
    return sendData('POST', url, optional)
}

export function usePatch<T>(url: string, id: number, data: Partial<T>): Promise<T | never> {
    const optional: { [key: string]: unknown } = {
        id: id,
        data: data,
    }
    return sendData('PATCH', url, optional)
}

export function useDelete(url: string, id: number) {
    return sendData('DELETE', url, {
        id: id,
    })
}
