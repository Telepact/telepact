import { Parser } from 'prettier';

declare module 'prettier-plugin-uapi' {
    const languages: any[];
    const parsers: { [key: string]: Parser };
    const printers: { [key: string]: any };
}
