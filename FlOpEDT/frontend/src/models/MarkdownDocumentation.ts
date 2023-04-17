export class MarkdownDocumentation {
    private _textContent : string;
    private _paramCallCount : Map<string,number>

    constructor(textContent:string, paramCallCount:Map<string,number>){
        this._textContent = textContent
        this._paramCallCount = paramCallCount
    }

    get textContent(){
        return this._textContent
    }

    get paramCallCount(){
        return this._paramCallCount
    }


}