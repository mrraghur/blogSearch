const Typesense = require("typesense");
const _ = require("lodash");
module.exports = (async () => {
  const client = new Typesense.Client({
    nodes: [
      {
        host: "localhost",
        port: "8108",
        protocol: "http",
      },
    ],
    apiKey: "xyz",
  });

  const schema = {
    name: "blogs",
    fields: [
      { name: "title", type: "string" },
      { name: "category", type: "string", facet: true },
      { name: "url", type: "string" },
      { name: "description", type: "string" },
      { name: "text", type: "string" },
      { name: "readingtime", type: "int32", facet: true },
      { name: "aud", type: "string", facet: true },
      { name: "imgs", type: "string" },
    ],
  };
  const collections = await client.collections().retrieve();
  const collectionNames = collections.map((collection) => {
    return collection.name;
  });
  console.log(collectionNames);
  try {
    if (_.includes(collectionNames, schema.name) === false) {
      await client.collections().create(schema);
      console.log("Collection blogs created successfully");
    } else {
      console.log("Collection blogs already present");
    }
  } catch (error) {
    console.error(error);
  }
})();
