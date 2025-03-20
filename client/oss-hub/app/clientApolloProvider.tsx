// ClientApolloProvider.tsx
import React, { useEffect, useState } from "react";
import { Outlet } from "react-router";

export default function ClientApolloProvider() {
  const [client, setClient] = useState<any>(null);

  useEffect(() => {
    // Dynamically import Apollo Client
    import("@apollo/client").then((ApolloClientModule) => {
      const { ApolloClient, ApolloProvider, InMemoryCache } = ApolloClientModule;
      const apolloClient = new ApolloClient({
        uri: "http://192.168.49.2:31579/graphql",
        cache: new InMemoryCache({ assumeImmutableResults: true }),
        ssrMode: false,
      });
      setClient({ ApolloProvider, client: apolloClient });
    });
  }, []);

  if (!client) {
    return <div>Loading Apollo Client...</div>;
  }

  const { ApolloProvider } = client;
  return (
    <ApolloProvider client={client.client}>
      <Outlet />
    </ApolloProvider>
  );
}

