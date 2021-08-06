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
  var myArgs = process.argv.slice(2);
  const blogs = await require(myArgs[1]);
  try {
    const returnData = await client
      .collections(myArgs[0])
      .documents()
      .import(blogs);
    // console.log(returnData);
    // console.log('Done indexing.');

    const failedItems = returnData.filter((item) => item.success === false);
    const passedItems = returnData.filter((item) => item.success === true);
    if (failedItems.length > 0) {
      throw new Error(
        `Error indexing items ${JSON.stringify(failedItems, null, 2)}`
      );
    }
    console.log("No of documents added to collection: ", passedItems.length);

    return returnData;
  } catch (error) {
    console.log(error);
  }
})();
