// import {
//     GraphQLSchema,
//     graphql,
//     GraphQLObjectType,
//     GraphQLList,
//     GraphQLInt,
//     GraphQLString,
// } from "graphql"
// import {attributeFields, resolver} from "graphql-sequelize"
// import {createContext, EXPECTED_OPTIONS_KEY} from "dataloader-sequelize"

// import {Item, Metadata, sequelize} from "src/Models.js"

// const metadataType = new GraphQLObjectType({
//     name: "Metadata",
//     description: "Metadata for an item",
//     fields: attributeFields(Metadata),
// })
// const itemType = new GraphQLObjectType({
//     name: "Item",
//     description: "An item",
//     fields: {
//         ...attributeFields(Item),
//         // metadata: {
//         //     type: new GraphQLList(metadataType),
//         //     resolve: resolver(Item.Metadata),
//         // },
//     },
// })

// // const queryType = new GraphQLSchema({
// //     query: itemType,
// // })

// // const resolvers = {
// //     Query: {
// //         item: resolver(models.Item),
// //         items: resolver(models.Item),
// //     },
// //     Item: {
// //         metadata: resolver(models.Item.Metadata),
// //     },
// // }

// let schema = new GraphQLSchema({
//     query: new GraphQLObjectType({
//         name: "RootQueryType",
//         fields: {
//             items: {
//                 // The resolver will use `findOne` or `findAll` depending on whether the field it's used in is a `GraphQLList` or not.
//                 type: new GraphQLList(itemType),
//                 args: {
//                     // An arg with the key limit will automatically be converted to a limit on the target
//                     limit: {
//                         type: GraphQLInt,
//                     },
//                     // An arg with the key order will automatically be converted to a order on the target
//                     order: {
//                         type: GraphQLString,
//                     },
//                     hash: {
//                         type: GraphQLString,
//                     },
//                 },
//                 resolve: resolver(Item),
//             },
//         },
//     }),
// })

import {ApolloServer, gql} from "apollo-server-micro"
import {attributeFields, resolver} from "graphql-sequelize"
import {createContext, EXPECTED_OPTIONS_KEY} from "dataloader-sequelize"
import {GraphQLScalarType} from "graphql"
import {Kind} from "graphql/language"

import {Item, Metadata, sequelize} from "src/Models.js"

const typeDefs = gql`
    scalar Date

    type Query {
        items(
            order: String = "reverse:created_at"
            limit: Int = 10
            offset: Int = 0
            bucket: String
            image: Boolean
        ): [Item]
        item(hashid: ID!): Item
    }
    type Metadata {
        content: String!
        kind: String
        url: Boolean
        url_name: String
    }
    type Item {
        id: ID
        text: String
        image: String
        timezone: String
        created_at: Date
        lat: Float
        lng: Float
        language: String
        bucket: String
        hashid: ID
        metadata: [Metadata]
    }
`

const resolvers = {
    Query: {
        items: resolver(Item, {
            before: (findOptions, args, context) => {
                if (args.offset) {
                    findOptions.offset = args.offset
                }
                return findOptions
            },
        }),
        item: resolver(Item),
    },
    Date: new GraphQLScalarType({
        name: "Date",
        description: "Date custom scalar type",
        parseValue(value) {
            return new Date(value) // value from the client
        },
        serialize(value) {
            console.log(value)
            return value.getTime() // value sent to the client
        },
        parseLiteral(ast) {
            if (ast.kind === Kind.INT) {
                return new Date(ast.value) // ast value is always in string format
            }
            return null
        },
    }),
    Item: {
        metadata: resolver(Item.Metadata),
    },
}

resolver.contextToOptions = {[EXPECTED_OPTIONS_KEY]: EXPECTED_OPTIONS_KEY}

const apolloServer = new ApolloServer({
    typeDefs,
    resolvers,
    context(req) {
        const dataloaderContext = createContext(sequelize)

        return {
            [EXPECTED_OPTIONS_KEY]: dataloaderContext,
        }
    },
})

export const config = {
    api: {
        bodyParser: false,
    },
}

export default apolloServer.createHandler({path: "/api/graphql"})
