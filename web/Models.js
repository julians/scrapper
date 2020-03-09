import Sequelize from "sequelize"

export const sequelize = new Sequelize({
    dialect: "sqlite",
    storage: "../scraps.db",
})

const Model = Sequelize.Model

export class Item extends Model {}
Item.init(
    {
        text: {
            type: Sequelize.TEXT,
            allowNull: false,
        },
        image: {
            type: Sequelize.STRING,
        },
        created_at: {
            type: Sequelize.DATE,
        },
        timezone: {
            type: Sequelize.STRING,
        },
        lat: {
            type: Sequelize.FLOAT,
        },
        lng: {
            type: Sequelize.FLOAT,
        },
        language: {
            type: Sequelize.STRING(5),
        },
        bucket: {
            type: Sequelize.STRING(16),
        },
        hashid: {
            type: Sequelize.STRING(40),
        },
    },
    {
        sequelize,
        modelName: "item",
        timestamps: false,
        tableName: "item",
    },
)

export class Metadata extends Model {}
Metadata.init(
    {
        content: {
            type: Sequelize.STRING,
            allowNull: false,
        },
        kind: {
            type: Sequelize.STRING,
        },
        url: {
            type: Sequelize.STRING,
        },
        url_name: {
            type: Sequelize.STRING,
        },
    },
    {
        sequelize,
        modelName: "metadata",
        timestamps: false,
        tableName: "metadata",
    },
)

export class ItemMetadata extends Model {}
ItemMetadata.init(
    {},
    {
        sequelize,
        modelName: "itemmetadata",
        timestamps: false,
        tableName: "itemmetadata",
    },
)

Item.Metadata = Item.belongsToMany(Metadata, {
    through: ItemMetadata,
    foreignKey: "item_id",
})
Metadata.belongsToMany(Item, {
    through: ItemMetadata,
    foreignKey: "metadata_id",
})
