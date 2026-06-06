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
      intro="Your Rank updates locally from applicant inputs, selected weights, cost basis, and reversible exclusions while Baseline Rank stays visible."
      limit={50}
    />
  );
}
