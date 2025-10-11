export interface TypedMessage<T> {
    headers: { [key: string]: any },
    body: T
}