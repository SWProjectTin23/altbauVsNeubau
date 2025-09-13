import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
  url: "http://localhost:8844/",
  realm: "timsicher",
  clientId: "frontend",
});

export default keycloak;
