import authMsgPact from '../../../inc/auth.msgpact.json';

export function getAuthMsgPactJson(): string {
    return JSON.stringify(authMsgPact);
}
