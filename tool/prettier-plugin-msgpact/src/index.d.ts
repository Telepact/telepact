import { Parser } from 'prettier';

declare module 'prettier-plugin-msgpact' {
    const languages: any[];
    const parsers: { [key: string]: Parser };
    const printers: { [key: string]: any };
}
