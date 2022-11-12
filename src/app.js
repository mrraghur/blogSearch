import TypesenseInstantSearchAdapter from "typesense-instantsearch-adapter";

const typesenseInstantsearchAdapter = new TypesenseInstantSearchAdapter({
  server: {
    apiKey: "xyz", // Be sure to use an API key that only allows searches, in production
    nodes: [
      {
        //host: "172.105.148.128",
        host: "search.interviewblindspots.com",
        //port: "8108",
        port: "80",
        protocol: "http",
      },
    ],
  },
  // The following parameters are directly passed to Typesense's search API endpoint.
  //  So you can pass any parameters supported by the search endpoint below.
  //  queryBy is required.
  //  filterBy is managed and overridden by InstantSearch.js. To set it, you want to use one of the filter widgets like refinementList or use the `configure` widget.
  additionalSearchParameters: {
    highlightAffixNumTokens: 20, // <============
    queryBy: "text,title,imgs,category",
  },
});

const Typesense = require("typesense");

let client = new Typesense.Client({
  nodes: [
    {
      //host: "172.105.148.128", // For Typesense Cloud use xxx.a1.typesense.net
      host: "search.interviewblindspots.com", // For Typesense Cloud use xxx.a1.typesense.net
      //port: "8108", // For Typesense Cloud use 443
      port: "80", // For Typesense Cloud use 443
      protocol: "http", // For Typesense Cloud use https
    },
  ],
  apiKey: "xyz",
  // connectionTimeoutSeconds: 2,
});

const searchClient = typesenseInstantsearchAdapter.searchClient;

const search = instantsearch({
  searchClient,
  indexName: "blogs",
  // routing: {
  //   stateMapping: instantsearch.stateMappings.singleIndex("blogs"),
  // },
  // https://stackoverflow.com/questions/37801289/how-do-i-set-algolia-to-not-return-any-results-if-the-query-is-blank
  searchFunction(helper) {
    const hits = document.querySelector("#hits");
    const pagination = document.querySelector("#pagination");
    const filter = document.querySelector(".filter-box");
    const empty = document.querySelector(".empty");
    const structuredResults = document.querySelector("#structuredResults");

    hits.style.display = helper.state.query === "" ? "none" : "";
    pagination.style.display = helper.state.query === "" ? "none" : "";
    filter.style.display = helper.state.query === "" ? "none" : "";
    empty.style.display = helper.state.query !== "" ? "none" : "";
    structuredResults.style.display = helper.state.query === "" ? "none" : "";

    // console.log(helper.state.query);
    let searchParams = {
      q: helper.state.query,
      query_by: "text",
      page: 1,
      per_page: 1,
      highlight_affix_num_tokens: 30,
    };
    if (helper.state.query) {
      	
	client
        .collections("structuredResults")
        .documents()
        .search(searchParams)
        .then(function(searchResults) {


          let element = `
        <div>
          <a href="${searchResults.hits[0].document.url}">About .....</a>
          <p>${searchResults.hits[0].document.url}</p>
          <p>${searchResults.hits[0].highlights[0].snippet}</p>
        </div>`;

          document.getElementById("structuredResults").innerHTML = element;
        });
	
    }

    helper.search();
  },
});



search.addWidgets([
  //////////////////////////

  //////////////////////////

  instantsearch.widgets.searchBox({
    container: "#searchbox",
    placeholder: "Search for Blogs... ",
  }),
  instantsearch.widgets.configure({
    hitsPerPage: 10,
    // attributesToSnippet: ['text']
  }),
  instantsearch.widgets.hits({
    container: "#hits",
    templates: {
      item: `
        <div>
        <div style="display:flex">

         <div style="flex:15%">
            <div>
           <img src={{#helpers.snippet}}{ "attribute": "imgs" }{{/helpers.snippet}}  style="width:100%;"/>
            </div>
        </div>

          <div style="flex:75%">
              <div class="hit-name"><a href={{url}}>
                {{#helpers.highlight}}{ "attribute": "title" }{{/helpers.highlight}}
                </a>
                <p>{{#helpers.snippet}}{ "attribute": "description" }{{/helpers.snippet}}</p>
                <p>{{#helpers.snippet}}{ "attribute": "text" }{{/helpers.snippet}}</p>
              </div>
              <div class="hit-authors">
                {{ category }}
              </div>
          </div>
        </div>
      `,
    },
  }),

  instantsearch.widgets.refinementList({
    limit: 5,
    showMore: true,
    showMoreLimit: 30,
    container: "#category",
    attribute: "category",
    searchable: true,
    searchablePlaceholder: "Search Categories",
    showMore: true,
    sortBy: ["name:asc", "count:desc"],
    cssClasses: {
      searchableInput: "search-categs-input",
    },
  }),
  instantsearch.widgets.refinementList({
    limit: 3,
    container: "#aud",
    attribute: "aud",
  }),
  instantsearch.widgets.rangeSlider({
    container: "#readingtime",
    attribute: "readingtime",
    step: 1,
  }),

  instantsearch.widgets.clearRefinements({
    container: "#clear-categs",
    templates: {
      resetLabel: "Clear filters",
    },
  }),
  instantsearch.widgets.pagination({
    container: "#pagination",
  }),
]);

search.start();
