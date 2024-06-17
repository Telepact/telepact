import { UFieldDeclaration } from 'uapi/internal/types/UFieldDeclaration';

export class UHeaders {
    name: string;
    requestHeaders: { [key: string]: UFieldDeclaration };
    responseHeaders: { [key: string]: UFieldDeclaration };

    constructor(
        name: string,
        requestHeaders: { [key: string]: UFieldDeclaration },
        responseHeaders: { [key: string]: UFieldDeclaration },
    ) {
        this.name = name;
        this.requestHeaders = requestHeaders;
        this.responseHeaders = responseHeaders;
    }
}
