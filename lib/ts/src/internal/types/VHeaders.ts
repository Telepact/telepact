import { VFieldDeclaration } from './VFieldDeclaration';

export class VHeaders {
    name: string;
    requestHeaders: { [key: string]: VFieldDeclaration };
    responseHeaders: { [key: string]: VFieldDeclaration };

    constructor(
        name: string,
        requestHeaders: { [key: string]: VFieldDeclaration },
        responseHeaders: { [key: string]: VFieldDeclaration },
    ) {
        this.name = name;
        this.requestHeaders = requestHeaders;
        this.responseHeaders = responseHeaders;
    }
}
