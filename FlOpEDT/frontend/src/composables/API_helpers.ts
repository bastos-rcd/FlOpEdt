export function build_url(url:string, ...contexts:any[]) {
    const full_context = contexts.reduce(
        function (acc, val) {
            return Object.assign(acc, val);
        },
        {}
    );
    return url + "?" + Object.keys(full_context).map(
        function (p) {
            return p + "=" + full_context[p];
        }
    ).join("&");
}