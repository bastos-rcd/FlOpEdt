import { MarkdownDocumentation } from "@/models/MarkdownDocumentation"

import { useFetch } from "@/composables/api"

/**
 * Load the documentation of the constraint
 * 
 * @param documentationName 
 * @param lang in which the doc should be loaded
 * @returns a Promise containing the MarkdownDocumentation 
 */
export async function queryDoc(documentationName: string, lang: string) {
    return new Promise((resolve, reject) => useFetch(`/${lang}/api/ttapp/docu/${documentationName}.md`, {}).then((response) => {
        const interpolationsCount = new Map<string, number>()
        Object.keys(response.inter).forEach(p => {
            interpolationsCount.set(p, response.inter[p])
        })
        const doc = new MarkdownDocumentation(response.text, interpolationsCount)
        resolve(doc)
    })
        .catch((error) => { 
            reject(error)
        }))
}
