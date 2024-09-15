import { convexAuthNextjsToken } from "@convex-dev/auth/nextjs/server";
import { fetchQuery } from "convex/nextjs";
import SurveyForm from "./HackerForm/HackathonProfileForm";
import { api } from "@/convex/_generated/api";

export default async function HomePage() {
  const viewer = await fetchQuery(
    api.users.viewer,
    {},
    { token: convexAuthNextjsToken() },
  );
  
  return <SurveyForm  viewer={viewer._id}/>;
}

