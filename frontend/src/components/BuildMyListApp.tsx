import type { ProductSchool } from "../lib/school-utils";
import { RecommendationFeed } from "./RecommendationFeed";

type Props = {
  schools: ProductSchool[];
  caveat: string;
};

export function BuildMyListApp({ schools, caveat }: Props) {
  return (
    <RecommendationFeed
      schools={schools}
      caveat={caveat}
      title="Schools to review first"
      intro="Cards update from generated ranking data, applicant score inputs, cost availability, and source-confidence filters."
      limit={18}
    />
  );
}
