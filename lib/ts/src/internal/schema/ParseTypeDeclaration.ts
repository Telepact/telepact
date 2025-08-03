//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { TTypeDeclaration } from '../types/TTypeDeclaration';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { TArray } from '../../internal/types/TArray';
import { TObject } from '../../internal/types/TObject';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { getOrParseType } from '../../internal/schema/GetOrParseType';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';

export function parseTypeDeclaration(
  path: Array<any>,
  typeDeclarationObject: any,
  ctx: any,
): TTypeDeclaration {
  if (typeof typeDeclarationObject === 'string') {
    const rootTypeString: string = typeDeclarationObject;

    const regexString = '^(.+?)(\\?)?$';
    const regex = new RegExp(regexString);

    const matcher = rootTypeString.match(regex);
    if (!matcher) {
      throw new TelepactSchemaParseError(
        [
          new SchemaParseFailure(
            ctx.documentName,
            path,
            'StringRegexMatchFailed',
            { regex: regexString }
          ),
        ],
        ctx.telepactSchemaDocumentNamesToJson
      );
    }

    const typeName = matcher[1];
    const nullable = matcher[2] !== undefined;

    const tType = getOrParseType(path, typeName, ctx);

    if (tType.getTypeParameterCount() !== 0) {
      throw new TelepactSchemaParseError(
        [
          new SchemaParseFailure(
            ctx.documentName,
            path,
            'ArrayLengthUnexpected',
            { actual: 1, expected: tType.getTypeParameterCount() + 1 }
          ),
        ],
        ctx.telepactSchemaDocumentNamesToJson
      );
    }

    return new TTypeDeclaration(tType, nullable, []);
  } else if (Array.isArray(typeDeclarationObject)) {
    const listObject: Array<any> = typeDeclarationObject;

    if (listObject.length !== 1) {
      throw new TelepactSchemaParseError(
        [
          new SchemaParseFailure(
            ctx.documentName,
            path,
            'ArrayLengthUnexpected',
            { actual: listObject.length, expected: 1 }
          ),
        ],
        ctx.telepactSchemaDocumentNamesToJson
      );
    }

    const elementTypeDeclaration = listObject[0];
    const newPath = [...path, 0];

    const arrayType = new TArray();
    const parsedElementType = parseTypeDeclaration(newPath, elementTypeDeclaration, ctx);

    return new TTypeDeclaration(arrayType, false, [parsedElementType]);
  } else if (typeof typeDeclarationObject === 'object' && typeDeclarationObject !== null) {
    const mapObject: Record<string, any> = typeDeclarationObject;

    const keys = Object.keys(mapObject);
    if (keys.length !== 1) {
      throw new TelepactSchemaParseError(
        [
          new SchemaParseFailure(
            ctx.documentName,
            path,
            'ObjectSizeUnexpected',
            { actual: keys.length, expected: 1 }
          ),
        ],
        ctx.telepactSchemaDocumentNamesToJson
      );
    }

    const key = keys[0];
    const value = mapObject[key];

    if (key !== 'string') {
      const keyPath = [...path, 'key'];
      throw new TelepactSchemaParseError(
        [
          new SchemaParseFailure(
            ctx.documentName,
            path,
            'RequiredObjectKeyMissing',
            { key: 'string' }
          ),
          new SchemaParseFailure(ctx.documentName, keyPath, 'ObjectKeyDisallowed', {}),
        ],
        ctx.telepactSchemaDocumentNamesToJson
      );
    }

    const newPath = [...path, key];

    const objectType = new TObject();
    const parsedValueType = parseTypeDeclaration(newPath, value, ctx);

    return new TTypeDeclaration(objectType, false, [parsedValueType]);
  } else {
    const failures = getTypeUnexpectedParseFailure(
      ctx.documentName,
      path,
      typeDeclarationObject,
      'StringOrArrayOrObject'
    );
    throw new TelepactSchemaParseError(failures, ctx.telepactSchemaDocumentNamesToJson);
  }
}