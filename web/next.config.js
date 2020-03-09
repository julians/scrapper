const path = require("path")

module.exports = {
    webpack(config, options) {
        config.resolve.alias["components"] = path.join(__dirname, "components")
        config.resolve.alias["src"] = path.join(__dirname)
        return config
    },
}
