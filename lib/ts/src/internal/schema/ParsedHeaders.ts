import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';

export class ParsedHeaders {
    requestHeaders: { [key: string]: UFieldDeclaration };
    responseHeaders: { [key: string]: UFieldDeclaration };

    constructor(
        requestHeaders: { [key: string]: UFieldDeclaration },
        responseHeaders: { [key: string]: UFieldDeclaration },
    ) {
        this.requestHeaders = requestHeaders;
        this.responseHeaders = responseHeaders;
    }
}
